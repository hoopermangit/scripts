import json
import os
import shutil
import subprocess
import time
from typing import Any, Dict, List

TARGET_ROOT = "/mnt/void"

class InstallationBackend:
    def __init__(self, target_root=TARGET_ROOT, log_callback=None):
        self.target_root = target_root
        self.log_callback = log_callback or print

    def _log(self, m): 
        if self.log_callback: self.log_callback(m)
        else: print(m)

    def _run(self, cmd, check=True, capture=False, chroot=False):
        if chroot: cmd = ["chroot", self.target_root] + cmd
        self._log(f"$ {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, check=check, text=True, capture_output=True)
            if capture: return res
            if res.stdout and len(res.stdout) < 300: self._log(f"OUT: {res.stdout.strip()}")
            if res.stderr:
                if "warning" in res.stderr.lower() or "information" in res.stderr.lower(): pass
                else: self._log(f"LOG: {res.stderr.strip()}")
            return res
        except subprocess.CalledProcessError as e:
            self._log(f"!! FEHLER (Exit {e.returncode}): {e}")
            if e.stderr: self._log(f"DETAILS: {e.stderr.strip()}")
            if check: raise
            return e

    # --- HELFER ---
    def _ensure_device_free(self, dev):
        self._log(f"Bereite Gerät {dev} vor (Unmount/Swapoff)...")
        self._run(["swapoff", "-a"], check=False)
        try:
            out = self._run(["lsblk", "-n", "-l", "-o", "NAME", dev], capture=True, check=False)
            if out and out.stdout:
                for p in out.stdout.split():
                    self._run(["umount", "-f", f"/dev/{p}"], check=False)
                    self._run(["dmsetup", "remove", p], check=False)
        except: pass
        time.sleep(1)

    # --- PARTITIONIERUNG ---
    def apply_partitioning(self, plan):
        dev = plan["device"]
        self._ensure_device_free(dev)
        
        if plan["mode"] == "erase":
            return self._part_erase(plan)
        else:
            return self._part_freespace(plan)

    def _part_erase(self, plan):
        dev = plan["device"]
        uefi = plan["uefi"]
        
        self._log(f"Lösche Festplatte {dev}...")
        self._run(["wipefs", "-a", "-f", dev])
        self._run(["udevadm", "settle"], check=False)
        time.sleep(1)
        
        label = "gpt" if uefi else "msdos"
        # Retry mklabel
        for i in range(3):
            try:
                self._run(["parted", "-s", dev, "mklabel", label])
                break
            except:
                time.sleep(2)
                self._ensure_device_free(dev)
        
        return self._create_layout(dev, uefi, "1MiB", "100%", plan)

    def _part_freespace(self, plan):
        dev = plan["device"]
        self._log(f"Suche freien Speicher auf {dev}...")
        
        res = self._run(["parted", "-m", dev, "unit", "MiB", "print", "free"], capture=True)
        if not res or not res.stdout: raise Exception("Partitionstabelle nicht lesbar")

        best_start, best_end, max_size = None, None, 0.0
        for line in res.stdout.strip().splitlines():
            if line.strip().endswith(";free;"):
                p = line.split(":")
                try:
                    sz = float(p[3].replace("MiB", ""))
                    if sz > max_size:
                        max_size = sz
                        best_start, best_end = p[1], p[2]
                except: pass
        
        if max_size < 10000: raise Exception("Zu wenig freier Speicher (<10GB).")
        self._log(f"Nutze Bereich: {best_start} - {best_end}")
        return self._create_layout(dev, plan["uefi"], best_start, best_end, plan)

    def _create_layout(self, dev, uefi, start, end, plan):
        parts = {}
        # Freie ID finden
        out = self._run(["lsblk", "-n", "-l", "-o", "NAME", dev], capture=True, check=False).stdout or ""
        idx = 1
        while True:
            pn = self._devp(dev, idx)
            if os.path.basename(pn) not in out and not os.path.exists(pn): break
            idx += 1
        
        try: s_val = float(start.replace("MiB", ""))
        except: s_val = 1.0
        
        # 1. EFI
        if uefi:
            e_val = s_val + 512
            self._run(["parted", "-s", dev, "mkpart", "primary", "fat32", f"{s_val}MiB", f"{e_val}MiB"])
            self._run(["parted", "-s", dev, "set", str(idx), "esp", "on"])
            parts[self._devp(dev, idx)] = {"mountpoint": "/boot/efi", "fs": "vfat"}
            idx += 1; s_val = e_val

        # 2. Swap
        if plan.get("use_swap"):
            e_val = s_val + 8192
            self._run(["parted", "-s", dev, "mkpart", "primary", "linux-swap", f"{s_val}MiB", f"{e_val}MiB"])
            parts[self._devp(dev, idx)] = {"mountpoint": "[SWAP]", "fs": "swap"}
            idx += 1; s_val = e_val
            
        # 3. Root & Home
        try: total_end = 999999.0 if "%" in end else float(end.replace("MiB", ""))
        except: total_end = 999999.0
        
        fs = plan["filesystem"]
        if plan.get("use_home") and total_end > s_val + 20000: 
            home_sz = plan["home_size"] * 1024
            if str(end) == "100%":
                # Erase Mode
                split = f"-{plan['home_size']}GiB"
                self._run(["parted", "-s", dev, "mkpart", "primary", fs, f"{s_val}MiB", split])
                parts[self._devp(dev, idx)] = {"mountpoint": "/", "fs": fs}
                idx += 1
                self._run(["parted", "-s", dev, "mkpart", "primary", fs, split, "100%"])
                parts[self._devp(dev, idx)] = {"mountpoint": "/home", "fs": fs}
            else:
                # Freespace Mode
                split = total_end - home_sz
                self._run(["parted", "-s", dev, "mkpart", "primary", fs, f"{s_val}MiB", f"{split}MiB"])
                parts[self._devp(dev, idx)] = {"mountpoint": "/", "fs": fs}
                idx += 1
                self._run(["parted", "-s", dev, "mkpart", "primary", fs, f"{split}MiB", f"{total_end}MiB"])
                parts[self._devp(dev, idx)] = {"mountpoint": "/home", "fs": fs}
        else:
            end_arg = "100%" if end=="100%" else f"{total_end}MiB"
            self._run(["parted", "-s", dev, "mkpart", "primary", fs, f"{s_val}MiB", end_arg])
            parts[self._devp(dev, idx)] = {"mountpoint": "/", "fs": fs}

        self._run(["udevadm", "settle"])
        time.sleep(2)
        
        # Formatieren
        for d, i in parts.items(): 
            if not os.path.exists(d): time.sleep(2)
            self._mkfs(d, i["fs"])
        
        # Btrfs Subvols
        if fs == "btrfs":
            root = next((d for d,i in parts.items() if i["mountpoint"] == "/"), None)
            if root: self._btrfs_subvols(root, parts, plan.get("use_home"))
            
        return parts

    def _devp(self, d, i): return f"{d}p{i}" if "nvme" in d or "mmcblk" in d else f"{d}{i}"
    
    def _mkfs(self, d, fs):
        self._log(f"Format {d} ({fs})")
        if fs=="vfat": self._run(["mkfs.vfat","-F32",d])
        elif fs=="swap": self._run(["mkswap",d])
        elif fs=="btrfs": self._run(["mkfs.btrfs","-f",d])
        elif fs=="xfs": self._run(["mkfs.xfs","-f",d])
        else: self._run(["mkfs.ext4","-F",d])

    def _btrfs_subvols(self, dev, parts, has_home):
        m = "/tmp/btrfs_gen"
        os.makedirs(m, exist_ok=True)
        self._run(["mount", dev, m])
        subs = ["@", "@snapshots"]
        if not has_home: subs.append("@home")
        for s in subs: 
            if not os.path.exists(f"{m}/{s}"): self._run(["btrfs", "subvolume", "create", f"{m}/{s}"])
        self._run(["umount", m])
        parts[dev]["subvol"] = "@"
        if not has_home: parts["VIRTUAL_HOME"] = {"device": dev, "mountpoint": "/home", "subvol": "@home"}

    # --- MOUNT & COPY ---
    def _mount_filesystems(self, plan):
        # FIX: Plan entpacken, da View self.plan übergibt
        if "manual_partitions" in plan:
            parts = plan["manual_partitions"]
        else:
            parts = plan # Fallback falls nur parts übergeben wurden
            
        # 1. Root
        root_dev = next(d for d,i in parts.items() if i["mountpoint"]=="/")
        info = parts[root_dev]
        opts = f"defaults,subvol={info['subvol']}" if "subvol" in info else "defaults"
        if info.get("fs") == "btrfs": opts += ",compress=zstd"
        self._mount(root_dev, self.target_root, opts)
        
        # 2. Virtual Home
        if "VIRTUAL_HOME" in parts:
            v = parts["VIRTUAL_HOME"]
            self._mount(v["device"], f"{self.target_root}/home", f"defaults,compress=zstd,subvol={v['subvol']}")
            
        # 3. Others
        for d,i in parts.items():
            if d=="VIRTUAL_HOME" or i["mountpoint"] in ["/","[SWAP]"]: continue
            opts = "defaults,umask=0077" if i.get("fs")=="vfat" else "defaults"
            self._mount(d, f"{self.target_root}{i['mountpoint']}", opts)
            
        # Swap
        swp = next((d for d,i in parts.items() if i["mountpoint"]=="[SWAP]"), None)
        if swp: self._run(["swapon", swp])

    def _mount(self, d, p, o=None):
        os.makedirs(p, exist_ok=True)
        cmd = ["mount"]
        if o: cmd += ["-o", o]
        cmd += [d, p]
        self._run(cmd)

    def _copy_live_filesystem(self):
        self._log("Kopiere System (rsync)...")
        ex = ["/proc/*", "/sys/*", "/dev/*", "/run/*", "/tmp/*", "/mnt/*", "/media/*", 
              "/etc/fstab", "/etc/crypttab", "/home/anon", "/boot/grub/grub.cfg", 
              "/var/cache/xbps/*", "/var/db/xbps/keys/*"]
        
        if shutil.which("rsync"):
            cmd = ["rsync", "-aHAX", "--info=progress2"]
            for e in ex: cmd.extend(["--exclude", e])
            cmd.extend(["/", self.target_root])
            res = self._run(cmd, check=False)
            if res.returncode not in [0, 23, 24]: raise Exception(f"rsync failed: {res.returncode}")
        else:
            e = " ".join([f"--exclude='{x}'" for x in ex])
            subprocess.run(f"tar {e} -cf - / | tar -xf - -C {self.target_root}", shell=True, check=True)

    # --- CONFIG ---
    def _generate_fstab(self, _):
        res = self._run(["findmnt", "-R", "-n", "-o", "TARGET,UUID,FSTYPE,OPTIONS", self.target_root], capture=True)
        with open(f"{self.target_root}/etc/fstab", "w") as f:
            f.write("# Generated by Installer\n")
            if res and res.stdout:
                for l in res.stdout.splitlines():
                    parts = l.split()
                    if len(parts) < 4: continue
                    t, u, fs, o = parts[0], parts[1], parts[2], parts[3]
                    if t == self.target_root: t = "/"
                    else: t = t.replace(self.target_root, "")
                    t = ''.join(char for char in t if char.isprintable() and char not in '└─┘│┌┐├┤┬┴┼')
                    if not t: continue
                    f.write(f"UUID={u}\t{t}\t{fs}\t{o}\t0 0\n")

    def _configure_basics(self, plan):
        with open(f"{self.target_root}/etc/hostname", "w") as f: f.write(plan["user"]["hostname"])
        with open(f"{self.target_root}/etc/locale.conf", "w") as f: f.write(f"LANG={plan['language']}\n")
        with open(f"{self.target_root}/etc/rc.conf", "a") as f: f.write(f"KEYMAP={plan['keyboard']}\n")
        if os.path.exists(f"{self.target_root}/etc/localtime"): os.remove(f"{self.target_root}/etc/localtime")
        self._run(["ln", "-sf", f"/usr/share/zoneinfo/{plan['timezone']}", f"{self.target_root}/etc/localtime"])
        
        lf = f"{self.target_root}/etc/default/libc-locales"
        if os.path.exists(lf):
            with open(lf, "r") as f: c = f.read()
            l = plan["language"]
            c = c.replace(f"# {l}", l).replace(f"#{l}", l)
            with open(lf, "w") as f: f.write(c)

    def _configure_user(self, plan):
        u = plan["user"]
        self._enter_chroot()
        try:
            self._run(["userdel", "-r", "anon"], chroot=True, check=False)
            p = subprocess.Popen(["chroot", self.target_root, "passwd", "root"], stdin=subprocess.PIPE, text=True)
            p.communicate(f"{u['root_password']}\n{u['root_password']}\n")
            
            self._run(["useradd", "-m", "-s", "/bin/bash", "-G", "wheel,users,audio,video,network,input,storage", u['name']], chroot=True)
            p = subprocess.Popen(["chroot", self.target_root, "passwd", u['name']], stdin=subprocess.PIPE, text=True)
            p.communicate(f"{u['password']}\n{u['password']}\n")
            
            with open(f"{self.target_root}/etc/sudoers.d/wheel", "w") as f: f.write("%wheel ALL=(ALL:ALL) ALL\n")
            os.chmod(f"{self.target_root}/etc/sudoers.d/wheel", 0o440)
        finally: self._leave_chroot()

    def _finalize(self):
        self._enter_chroot()
        try: self._run(["xbps-reconfigure", "-fa"], chroot=True)
        finally: self._leave_chroot()

    def _bootloader(self, plan):
        self._enter_chroot()
        try:
            if plan["uefi"]: self._run(["grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi", "--bootloader-id=void", "--recheck"], chroot=True)
            else: self._run(["grub-install", "--target=i386-pc", plan["device"]], chroot=True)
            self._run(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], chroot=True)
        finally: self._leave_chroot()

    def _enter_chroot(self):
        for d in ["proc","sys","dev"]: 
            t = f"{self.target_root}/{d}"
            if not os.path.ismount(t): 
                self._run(["mount","--rbind",f"/{d}",t], check=False)
                self._run(["mount","--make-rslave",t], check=False)
        if os.path.exists("/sys/firmware/efi/efivars"):
             t = f"{self.target_root}/sys/firmware/efi/efivars"
             if not os.path.ismount(t): self._run(["mount", "--bind", "/sys/firmware/efi/efivars", t], check=False)
        try: shutil.copy("/etc/resolv.conf", f"{self.target_root}/etc/resolv.conf")
        except: pass

    def _leave_chroot(self):
        for d in ["sys/firmware/efi/efivars", "dev", "sys", "proc"]: 
            self._run(["umount","-R",f"{self.target_root}/{d}"], check=False)

