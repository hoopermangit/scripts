import json
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.request
from typing import Any, Dict, List, Optional

TARGET_ROOT = "/mnt/void"


class InstallationBackend:
    def __init__(self, target_root: str = TARGET_ROOT, log_callback=None):
        self.target_root = target_root
        self.log_callback = log_callback or self._default_log
        self._binds_active = False

    def _default_log(self, msg: str):
        # When there is no callback use default logging function
        print(f"[InstallationBackend] {msg}")

    def _log(self, msg: str):
        # When there is a callback use callback for logging
        self.log_callback(msg)

    def _get_partition_device(self, device: str, part_num: int) -> str:
        # Get the correct partition device path and partition number
        if device.startswith("/dev/nvme"):
            return f"{device}p{part_num}"
        else:
            return f"{device}{part_num}"

    def _run(
        self, cmd: List[str], check=True, capture=False, chroot=False
    ) -> subprocess.CompletedProcess:
        if chroot:
            cmd = ["chroot", self.target_root] + cmd
        self._log(f"$ {' '.join(cmd)}")
        try:
            if capture:
                result = subprocess.run(
                    cmd, check=check, text=True, capture_output=True
                )
                if result.stderr:
                    self._log(f"STDERR: {result.stderr}")
                return result
            else:
                result = subprocess.run(
                    cmd, check=check, text=True, capture_output=True
                )
                if result.stdout:
                    self._log(f"STDOUT: {result.stdout}")
                if result.stderr:
                    self._log(f"STDERR: {result.stderr}")
                return result
        except subprocess.CalledProcessError as e:
            out = (getattr(e, "stdout", "") or "") + (getattr(e, "stderr", "") or "")
            self._log(f"!! BEFEHL FEHLGESCHLAGEN (Exit Code {e.returncode}): {e}")
            if out.strip():
                self._log(f"!! OUTPUT: {out}")
            if check:
                raise
            return e

    def _is_mounted(self, path: str) -> bool:
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == path:
                        return True
                return False
        except Exception as e:
            self._log(f"Warnung: Konnte /proc/mounts nicht lesen: {e}")
            return False

    def _mount_partition_safe(self, device: str, mountpoint: str, partition_name: str):
        self._log(f"Mounte {partition_name}-Partition: {device} → {mountpoint}")

        # Try multiple recovery strategies if mounting fails
        recovery_strategies = [
            ("Standard Mount", self._try_standard_mount),
            ("Force Mount with fsck", self._try_mount_with_fsck),
            ("Mount with explicit filesystem", self._try_mount_explicit_fs),
            ("Read-only Mount", self._try_readonly_mount),
        ]

        for strategy_name, strategy_func in recovery_strategies:
            try:
                self._log(f"Versuche {strategy_name} für {device}")
                if strategy_func(device, mountpoint, partition_name):
                    self._log(
                        f"✓ {partition_name}-Partition mit {strategy_name} erfolgreich gemountet"
                    )
                    return
            except Exception as e:
                self._log(f"✗ {strategy_name} fehlgeschlagen: {e}")
                continue

        raise Exception(
            f"Alle Mount-Strategien für {partition_name}-Partition fehlgeschlagen"
        )

    def _try_standard_mount(
        self, device: str, mountpoint: str, partition_name: str
    ) -> bool:
        # Try standard mount
        # Wait for device to be ready
        if not self._wait_for_device(device):
            return False

        # Check if device exists
        if not os.path.exists(device):
            self._log(f"Gerät {device} existiert nicht")
            return False

        # Check if already mounted
        if self._is_mounted(mountpoint):
            self._log(
                f"Warnung: {mountpoint} ist bereits gemountet, versuche unmount..."
            )
            self._run(["umount", mountpoint], check=False)

        # Ensure mountpoint exists
        os.makedirs(mountpoint, exist_ok=True)

        # Check filesystem before mounting
        result = self._run(["file", "-s", device], capture=True, check=False)
        fs_info = result.stdout.strip()
        self._log(f"Dateisystem auf {device}: {fs_info}")

        # Attempt mount
        self._run(["mount", device, mountpoint])

        # Verify mount succeeded
        return self._is_mounted(mountpoint)

    def _try_mount_with_fsck(
        self, device: str, mountpoint: str, partition_name: str
    ) -> bool:
        # Try mounting after filesystem check
        try:
            self._log(f"Führe Dateisystem-Check durch auf {device}")
            # Try to repair filesystem first
            self._run(["fsck", "-y", device], check=False)
            return self._try_standard_mount(device, mountpoint, partition_name)
        except:
            return False

    def _try_mount_explicit_fs(
        self, device: str, mountpoint: str, partition_name: str
    ) -> bool:
        # Try mounting with explicit filesystem type
        try:
            # Get filesystem type
            result = self._run(
                ["blkid", "-s", "TYPE", "-o", "value", device],
                capture=True,
                check=False,
            )
            fs_type = result.stdout.strip()
            if fs_type:
                self._log(f"Versuche Mount mit explizitem FS-Typ: {fs_type}")
                os.makedirs(mountpoint, exist_ok=True)
                self._run(["mount", "-t", fs_type, device, mountpoint])
                return self._is_mounted(mountpoint)
        except:
            pass
        return False

    def _try_readonly_mount(
        self, device: str, mountpoint: str, partition_name: str
    ) -> bool:
        # Try read-only mount as last resort
        try:
            self._log(f"Versuche Read-Only Mount für {device}")
            os.makedirs(mountpoint, exist_ok=True)
            self._run(["mount", "-o", "ro", device, mountpoint])
            if self._is_mounted(mountpoint):
                self._log(f"Warnung: {partition_name} nur als Read-Only gemountet!")
                return True
        except:
            pass
        return False

    def _wait_for_device(self, device: str, max_wait: int = 30):
        # Wait until device is ready

        self._log(f"Warte auf Gerät {device}...")

        for attempt in range(max_wait):
            if os.path.exists(device):
                # Device exists, check if it's readable
                try:
                    with open(device, "rb") as f:
                        f.read(512)  # Try to read first sector
                    self._log(f"Gerät {device} ist bereit nach {attempt + 1} Sekunden")
                    return True
                except (OSError, IOError) as e:
                    if attempt < max_wait - 1:
                        time.sleep(1)
                        continue
                    else:
                        self._log(f"Gerät {device} nicht lesbar nach {max_wait}s: {e}")
                        break
            else:
                if attempt < max_wait - 1:
                    time.sleep(1)
                else:
                    self._log(f"Gerät {device} nicht verfügbar nach {max_wait}s")
                    break

        return False

    def _verify_filesystem(self, device: str, expected_fs: str = None) -> bool:
        # Check if filesystem on device is properly formatted and accessible
        try:
            self._log(f"Verifiziere Dateisystem auf {device}...")

            result = self._run(["file", "-s", device], capture=True, check=False)
            fs_info = result.stdout.strip().lower()

            # Check for filesystem signatures
            if (
                "filesystem" not in fs_info
                and "ext" not in fs_info
                and "btrfs" not in fs_info
            ):
                self._log(
                    f"Warnung: Keine erkennbare Dateisystem-Signatur auf {device}"
                )
                return False

            # Use blkid to get filesystem type
            try:
                result = self._run(
                    ["blkid", "-s", "TYPE", "-o", "value", device],
                    capture=True,
                    check=False,
                )
                fs_type = result.stdout.strip()
                if fs_type:
                    self._log(f"Erkanntes Dateisystem: {fs_type}")
                    if expected_fs and fs_type != expected_fs:
                        self._log(
                            f"Warnung: Erwartet {expected_fs}, gefunden {fs_type}"
                        )
                else:
                    self._log(f"Kein Dateisystem-Typ von blkid erkannt")
            except:
                self._log(f"blkid konnte Dateisystem-Typ nicht ermitteln")

            return True

        except Exception as e:
            self._log(f"Dateisystem-Verifikation fehlgeschlagen: {e}")
            return False

    def _unmount_all_on_device(self, device: str):
        self._log(f"Prüfe und deaktiviere alle Mounts und Volumes auf {device}...")
        try:
            # Unmount all normal partitions and disable swap
            out = self._run(
                ["lsblk", "-Jpno", "NAME,TYPE,FSTYPE,MOUNTPOINT", device], capture=True
            ).stdout
            data = json.loads(out)
            partitions = []

            def find_partitions(node):
                if node.get("type") == "part":
                    partitions.append(node)
                for child in node.get("children", []):
                    find_partitions(child)

            for dev_info in data.get("blockdevices", []):
                find_partitions(dev_info)

            # Unmount all mounted partitions
            for part in reversed(partitions):
                path = part["name"]
                mountpoint = part.get("mountpoint")
                if mountpoint and mountpoint != "":
                    self._log(f"Unmounting {path} from {mountpoint}")
                    self._run(["umount", "-f", "-l", path], check=False)
                if part.get("fstype") == "swap":
                    self._log(f"Disabling swap on {path}")
                    self._run(["swapoff", path], check=False)

            # Force unmount any remaining mounts
            for part in reversed(partitions):
                path = part["name"]
                if self._is_mounted(path):
                    self._log(f"Force unmounting {path}")
                    self._run(["umount", "-f", "-l", path], check=False)

            # Deactivate LVM Volume Groups that use this device
            try:
                # Get partitions using lsblk
                out = self._run(
                    ["lsblk", "-Jpno", "NAME,TYPE,FSTYPE,MOUNTPOINT", device],
                    capture=True,
                ).stdout
                data = json.loads(out)
                partitions = []

                def find_partitions(node):
                    if node.get("type") == "part":
                        partitions.append(node)
                    for child in node.get("children", []):
                        find_partitions(child)

                for dev_info in data.get("blockdevices", []):
                    find_partitions(dev_info)

                self._log(f"Gefundene Partitionen: {[p['name'] for p in partitions]}")

                # Check each partition for LVM
                for partition in partitions:
                    part_device = partition["name"]
                    try:
                        pvs_out = self._run(
                            ["pvs", "--noheadings", "-o", "vg_name", part_device],
                            capture=True,
                            check=False,
                        )
                        if pvs_out.returncode == 0 and pvs_out.stdout.strip():
                            vg_name = pvs_out.stdout.strip()
                            self._log(
                                f"Deaktiviere LVM Volume Group '{vg_name}' von Partition {part_device}..."
                            )
                            self._run(["vgchange", "-an", vg_name], check=False)
                    except Exception as e:
                        self._log(f"LVM-Check für {part_device}: {e}")

                # Try a general LVM scan to catch any missed VGs
                try:
                    self._run(["vgchange", "-an"], check=False)  # Deactivate all VGs
                    self._log("Alle LVM Volume Groups deaktiviert")
                except Exception as e:
                    self._log(f"Generelle LVM-Deaktivierung: {e}")

            except Exception as e:
                self._log(f"LVM-Deaktivierung fehlgeschlagen: {e}")

        except Exception as e:
            self._log(f"Warnung beim Versuch, {device} aufzuräumen: {e}")

    def _apply_auto_partitioning_erase(self, plan: Dict[str, Any]):
        device = plan.get("device")
        layout = plan.get("auto_layout", {})
        if not device or not layout:
            raise ValueError("Plan für automatische Partitionierung unvollständig.")

        self._unmount_all_on_device(device)

        self._log(f"!!! DESTRUKTIVE AKTION: LÖSCHE ALLE DATEN AUF {device} !!!")

        # Additional safety: Force unmount any remaining mounts and disable swap
        self._log("Deaktiviere alle Swap-Partitionen...")
        self._run(["swapoff", "-a"], check=False)
        self._log("Hänge alle relevanten Dateisysteme aus...")
        self._run(
            ["umount", "-a", "--types", "ext4,ext3,ext2,xfs,btrfs,vfat,ntfs"],
            check=False,
        )

        # Wait for the system to release the device

        time.sleep(1)

        # Try to wipe the device with force flag
        try:
            self._run(["wipefs", "-a", "-f", device])
        except subprocess.CalledProcessError:
            self._log("wipefs failed, trying alternative approach...")
            # usedd if wipefs failed
            self._run(
                ["dd", "if=/dev/zero", f"of={device}", "bs=512", "count=1024"],
                check=False,
            )
        self._run(
            ["parted", "-s", device, "mklabel", "gpt" if plan.get("uefi") else "msdos"]
        )

        assignments = {}
        part_num = 1
        start_pos = "1MiB"
        if plan.get("uefi"):
            esp_size = layout.get("esp_size_mib", 512)
            end_pos = f"{esp_size + 1}MiB"
            self._run(
                [
                    "parted",
                    "-s",
                    device,
                    "mkpart",
                    "primary",
                    "fat32",
                    start_pos,
                    end_pos,
                ]
            )
            self._run(["parted", "-s", device, "set", str(part_num), "esp", "on"])
            assignments[self._get_partition_device(device, part_num)] = {
                "mountpoint": "/boot/efi",
                "format": True,
                "format_fs": "vfat",
            }
            part_num += 1
            start_pos = end_pos
        if layout.get("use_swap_partition"):
            swap_size = layout.get("swap_partition_gib", 8)
            # Convert swap size to MiB for consistency
            swap_size_mib = swap_size * 1024
            if plan.get("uefi"):
                esp_size = layout.get("esp_size_mib", 512)
                end_pos = f"{esp_size + 1 + swap_size_mib}MiB"
            else:
                end_pos = f"{1 + swap_size_mib}MiB"
            self._run(
                [
                    "parted",
                    "-s",
                    device,
                    "mkpart",
                    "primary",
                    "linux-swap",
                    start_pos,
                    end_pos,
                ]
            )
            assignments[self._get_partition_device(device, part_num)] = {
                "mountpoint": "[SWAP]",
                "format": True,
                "format_fs": "swap",
            }
            part_num += 1
            start_pos = end_pos
        fs_type = layout.get("filesystem", "btrfs")
        if layout.get("use_separate_home"):
            home_percent = layout.get("home_size_percent", 50)
            root_end_pos = f"{100 - home_percent}%"
            self._run(
                [
                    "parted",
                    "-s",
                    device,
                    "mkpart",
                    "primary",
                    fs_type,
                    start_pos,
                    root_end_pos,
                ]
            )
            assignments[self._get_partition_device(device, part_num)] = {
                "mountpoint": "/",
                "format": True,
                "format_fs": fs_type,
            }
            part_num += 1
            self._run(
                [
                    "parted",
                    "-s",
                    device,
                    "mkpart",
                    "primary",
                    fs_type,
                    root_end_pos,
                    "100%",
                ]
            )
            assignments[self._get_partition_device(device, part_num)] = {
                "mountpoint": "/home",
                "format": True,
                "format_fs": fs_type,
            }
        else:
            self._run(
                [
                    "parted",
                    "-s",
                    device,
                    "mkpart",
                    "primary",
                    fs_type,
                    start_pos,
                    "100%",
                ]
            )
            assignments[self._get_partition_device(device, part_num)] = {
                "mountpoint": "/",
                "format": True,
                "format_fs": fs_type,
            }
        self._run(["partprobe", device], check=False)

        # Format all partitions that need formatting
        self._log("Formatiere Partitionen...")
        for dev, assign in assignments.items():
            if assign.get("format"):
                fs_type = assign.get("format_fs", "ext4")
                self._make_fs(dev, fs_type)

        # Create btrfs subvolumes if using btrfs
        fs_type = layout.get("filesystem", "btrfs")
        if fs_type == "btrfs":
            # Find the root partition device
            root_dev = next(
                (d for d, a in assignments.items() if a.get("mountpoint") == "/"), None
            )
            if root_dev:
                self._create_btrfs_subvolumes(root_dev, plan)

        self._log(
            f"Automatische Partitionierung abgeschlossen. {len(assignments)} Partitionen erstellt."
        )
        return assignments

    def _get_uuid(self, device: str) -> str:
        try:
            res = self._run(
                ["blkid", "-s", "UUID", "-o", "value", device], capture=True
            )
            return res.stdout.strip()
        except subprocess.CalledProcessError:
            raise Exception(f"Konnte UUID für Gerät {device} nicht ermitteln.")

    def _make_fs(self, device: str, fs_type: str):
        self._log(f"Formatiere {device} als {fs_type}...")

        # For vfat, ensure device is unmounted and use -I flag to force initialization
        if fs_type == "vfat":
            # Check if device is mounted and unmount it
            if self._is_mounted(device):
                self._log(f"Gerät {device} ist gemountet, unmounte es...")
                self._run(["umount", "-f", "-l", device], check=False)
                # Wait a moment for unmount to complete
                time.sleep(1)

            # Use -I flag to force initialization even if device is not empty
            # -F32 specifies FAT32 format
            self._run(["mkfs.vfat", "-I", "-F32", device])
        elif fs_type == "btrfs":
            self._run(["mkfs.btrfs", "-f", device])
        elif fs_type == "ext4":
            self._run(["mkfs.ext4", "-F", device])
        elif fs_type == "xfs":
            self._run(["mkfs.xfs", "-f", device])
        elif fs_type == "swap":
            self._run(["mkswap", device])
        else:
            raise ValueError(f"Unbekanntes Dateisystem: {fs_type}")

    def _create_btrfs_subvolumes(self, device: str, plan: Dict[str, Any]):
        # Create btrfs subvolumes on the given device
        subvolumes = plan.get("auto_layout", {}).get("subvolumes", [])
        if not subvolumes:
            self._log("Keine Btrfs-Subvolumes konfiguriert.")
            return

        # Mapping from subvolume name to mount point
        subvol_mapping = {
            "@": "/",
            "@home": "/home",
            "@snapshots": "/.snapshots",
            "@var_log": "/var/log",
        }

        self._log(f"Erstelle Btrfs-Subvolumes auf {device}...")

        # Mount the root filesystem temporarily
        temp_mount = "/tmp/btrfs_temp"
        os.makedirs(temp_mount, exist_ok=True)
        try:
            self._run(["mount", device, temp_mount])

            # Create subvolumes
            for subvol_name in subvolumes:
                subvol_path = os.path.join(temp_mount, subvol_name)
                self._log(f"Erstelle Subvolume: {subvol_name}")
                self._run(["btrfs", "subvolume", "create", subvol_path])

                # Store mount point info for later mounting
                mount_point = subvol_mapping.get(subvol_name)
                if mount_point:
                    # Store this info in the plan for mounting phase
                    if "subvol_mounts" not in plan:
                        plan["subvol_mounts"] = {}
                    plan["subvol_mounts"][mount_point] = {
                        "device": device,
                        "subvol": subvol_name,
                    }

            self._log("✓ Btrfs-Subvolumes erstellt")
        finally:
            self._run(["umount", temp_mount], check=False)
            try:
                os.rmdir(temp_mount)
            except:
                pass

    def _mount_filesystems(self, plan):
        assignments = plan.get("manual_partitions", {})

        # Error message with debugging info
        if not assignments:
            mode = plan.get("mode", "unknown")
            auto_layout = plan.get("auto_layout", {})
            self._log(f"DEBUG: Mode = {mode}")
            self._log(f"DEBUG: Auto layout = {auto_layout}")
            self._log(f"DEBUG: Plan keys = {list(plan.keys())}")
            raise Exception(
                f"Keine Partitionen zum Einhängen gefunden. Modus: {mode}. Möglicherweise wurde die Partitionierung nicht korrekt abgeschlossen."
            )
        root_part, home_part, esp_part, swap_part = None, None, None, None
        for dev, assign in assignments.items():
            mp = assign.get("mountpoint")
            if mp == "/":
                root_part = dev
            elif mp == "/home":
                home_part = dev
            elif mp == "/boot/efi":
                esp_part = dev
            elif mp == "[SWAP]":
                swap_part = dev
        if not root_part:
            raise Exception("Keine Wurzelpartition (/) zugewiesen.")

        # Wait for all partitions to settle

        time.sleep(3)

        # Verify and mount root partition
        if not self._verify_filesystem(root_part):
            self._log(
                "Warnung: Root-Partition-Dateisystem nicht vollständig verifiziert"
            )

        # Check if we need to mount subvolumes
        subvol_mounts = plan.get("subvol_mounts", {})
        root_fs = assignments[root_part].get("format_fs", "ext4")

        if root_fs == "btrfs" and subvol_mounts:
            # Mount subvolumes instead of the whole filesystem
            self._log("Hänge Btrfs-Subvolumes ein...")

            # Mount root subvolume (@) as /
            root_subvol = subvol_mounts.get("/", {})
            if root_subvol:
                self._run(
                    [
                        "mount",
                        "-o",
                        f"subvol={root_subvol['subvol']}",
                        root_part,
                        self.target_root,
                    ]
                )
                self._log(f"✓ Root-Subvolume {root_subvol['subvol']} als / eingehängt")
            else:
                # Fallback: mount whole filesystem
                self._mount_partition_safe(root_part, self.target_root, "Root")

            # Mount other subvolumes
            for mount_point, mount_info in subvol_mounts.items():
                if mount_point == "/":
                    continue  # Already handled

                target_path = os.path.join(self.target_root, mount_point.lstrip("/"))
                os.makedirs(target_path, exist_ok=True)

                self._run(
                    [
                        "mount",
                        "-o",
                        f"subvol={mount_info['subvol']}",
                        mount_info["device"],
                        target_path,
                    ]
                )
                self._log(
                    f"✓ Subvolume {mount_info['subvol']} als {mount_point} eingehängt"
                )

            # Handle separate home partition if it exists (for non-btrfs cases)
            if home_part and "/home" not in subvol_mounts:
                home_mp = os.path.join(self.target_root, "home")
                os.makedirs(home_mp, exist_ok=True)
                if not self._verify_filesystem(home_part):
                    self._log(
                        "Warnung: Home-Partition-Dateisystem nicht vollständig verifiziert"
                    )
                self._mount_partition_safe(home_part, home_mp, "Home")
        else:
            # Standard mounting for non-btrfs or no subvolumes
            self._mount_partition_safe(root_part, self.target_root, "Root")

            # Mount home partition if exists
            if home_part:
                home_mp = os.path.join(self.target_root, "home")
                os.makedirs(home_mp, exist_ok=True)
                if not self._verify_filesystem(home_part):
                    self._log(
                        "Warnung: Home-Partition-Dateisystem nicht vollständig verifiziert"
                    )
                self._mount_partition_safe(home_part, home_mp, "Home")

        # Mount ESP partition if exists and UEFI
        if esp_part and plan.get("uefi"):
            esp_mp = os.path.join(self.target_root, "boot/efi")
            os.makedirs(esp_mp, exist_ok=True)
            if not self._verify_filesystem(esp_part, "vfat"):
                self._log("Warnung: ESP-Partition nicht als vfat verifiziert")
            self._mount_partition_safe(esp_part, esp_mp, "EFI System")
        if swap_part:
            self._run(["swapon", swap_part])

    def _generate_fstab(self, plan):
        self._log("Generiere /etc/fstab...")
        assignments = plan.get("manual_partitions", {})

        # Ensure /etc directory exists
        etc_dir = os.path.join(self.target_root, "etc")
        os.makedirs(etc_dir, exist_ok=True)

        with open(os.path.join(self.target_root, "etc/fstab"), "w") as f:
            f.write(
                "# /etc/fstab: static file system information.\n# <file system> <mount point> <type> <options> <dump> <pass>\n"
            )

            # Check if we have subvolumes to mount
            subvol_mounts = plan.get("subvol_mounts", {})
            root_dev = None
            root_fs = None

            for dev, assign in assignments.items():
                if assign.get("mountpoint") == "/":
                    root_dev = dev
                    root_fs = assign.get("format_fs", "ext4")
                    break

            # Write subvolume entries if using btrfs
            if root_fs == "btrfs" and subvol_mounts:
                for mount_point, mount_info in subvol_mounts.items():
                    uuid = self._get_uuid(mount_info["device"])
                    options = (
                        f"defaults,noatime,compress=zstd,subvol={mount_info['subvol']}"
                    )
                    dump_pass = "0 1" if mount_point == "/" else "0 2"
                    f.write(
                        f"UUID={uuid}\t{mount_point}\tbtrfs\t{options}\t{dump_pass}\n"
                    )
            else:
                # Standard fstab entries for non-btrfs
                for dev, assign in assignments.items():
                    if assign.get("mountpoint") == "/":
                        uuid = self._get_uuid(dev)
                        fs_type = assign.get("format_fs", "ext4")
                        options = (
                            "defaults,noatime,compress=zstd"
                            if fs_type == "btrfs"
                            else "defaults,noatime"
                        )
                        f.write(f"UUID={uuid}\t/\t{fs_type}\t{options}\t0 1\n")
                        break
                for dev, assign in assignments.items():
                    mp = assign.get("mountpoint")
                    if mp in ["/home", "/boot/efi"]:
                        uuid = self._get_uuid(dev)
                        fs_type = (
                            "vfat"
                            if mp == "/boot/efi"
                            else assign.get("format_fs", "ext4")
                        )
                        options = (
                            "defaults,noatime" if fs_type != "vfat" else "defaults"
                        )
                        f.write(f"UUID={uuid}\t{mp}\t{fs_type}\t{options}\t0 2\n")
                    elif mp == "[SWAP]":
                        uuid = self._get_uuid(dev)
                        f.write(f"UUID={uuid}\tnone\tswap\tsw\t0 0\n")
        self._log("fstab wurde geschrieben.")

    def _configure_mirror(self, plan):
        # Configure package mirrors for xbps
        self._log("Konfiguriere Paket-Mirrors...")

        # Get mirror URL directly from plan
        mirror_url = plan.get("mirror_url", "")

        if not mirror_url or mirror_url == "https://repo-default.voidlinux.org":
            self._log("Verwende Standard-Mirror-Konfiguration")
            return

        try:
            self._log(f"Konfiguriere Mirror: {mirror_url}")

            # Create xbps.d directory
            xbps_dir = os.path.join(self.target_root, "etc/xbps.d")
            os.makedirs(xbps_dir, exist_ok=True)

            # Write mirror configuration
            with open(os.path.join(xbps_dir, "00-repository-main.conf"), "w") as f:
                f.write(f"repository={mirror_url}/current\n")

            # Write multilib mirror if exists
            with open(os.path.join(xbps_dir, "10-repository-multilib.conf"), "w") as f:
                f.write(f"repository={mirror_url}/current/multilib\n")
                f.write(f"repository={mirror_url}/current/multilib/nonfree\n")

            # Write nonfree mirror
            with open(os.path.join(xbps_dir, "20-repository-nonfree.conf"), "w") as f:
                f.write(f"repository={mirror_url}/current/nonfree\n")

            self._log(f"✓ Mirror konfiguriert: {mirror_url}")

        except Exception as e:
            self._log(f"⚠ Fehler bei Mirror-Konfiguration: {e}")
            self._log("Verwende Standard-Mirror als Fallback")

    def _setup_xbps_config(self):
        # Setup XBPS configuration
        self._log("Setting up XBPS configuration...")

        # Check if target root exists
        if not os.path.exists(self.target_root):
            self._log(f"ERROR: Target root {self.target_root} does not exist")
            raise Exception(f"Target root {self.target_root} does not exist")

        # Create necessary directories
        xbps_cache_dir = os.path.join(self.target_root, "var/cache/xbps")
        xbps_db_dir = os.path.join(self.target_root, "var/db/xbps")
        xbps_keys_dir = os.path.join(self.target_root, "var/db/xbps/keys")
        usr_share_xbps_d = os.path.join(self.target_root, "usr/share/xbps.d")
        etc_xbps_d = os.path.join(self.target_root, "etc/xbps.d")

        for dir_path in [
            xbps_cache_dir,
            xbps_db_dir,
            xbps_keys_dir,
            usr_share_xbps_d,
            etc_xbps_d,
        ]:
            os.makedirs(dir_path, exist_ok=True)
            self._log(f"Created directory: {dir_path}")

        # Copy repository keys
        host_keys_dir = "/var/db/xbps/keys"
        if os.path.exists(host_keys_dir):
            for key_file in os.listdir(host_keys_dir):
                shutil.copy2(
                    os.path.join(host_keys_dir, key_file),
                    os.path.join(xbps_keys_dir, key_file),
                )
            self._log(f"Copied XBPS keys from {host_keys_dir}")

        # Test network connectivity
        self._log("Testing network connectivity...")
        try:
            urllib.request.urlopen("https://repo-default.voidlinux.org", timeout=10)
            self._log("Network connectivity: OK")
        except Exception as net_err:
            self._log(f"Network connectivity test failed: {net_err}")

    def _validate_packages(self, packages):
        # Validate packages exist in repositories and filter out invalid ones
        self._log(f"Validating {len(packages)} packages...")
        valid_packages = []
        invalid_packages = []

        for pkg in packages:
            # For essential packages, skip validation to speed up installation
            essential_packages = {
                "base-system",
                "grub",
                "grub-x86_64-efi",
                "bash",
                "curl",
                "git",
                "NetworkManager",
            }
            if pkg in essential_packages:
                valid_packages.append(pkg)
                continue

            # Check if package exists in repositories
            try:
                result = subprocess.run(
                    ["xbps-query", "-R", pkg], capture_output=True, text=True
                )
                if result.returncode == 0:
                    valid_packages.append(pkg)
                else:
                    self._log(f"Package '{pkg}' not found in repositories")
                    invalid_packages.append(pkg)
            except Exception as e:
                self._log(f"Error checking package '{pkg}': {e}, skipping")
                invalid_packages.append(pkg)

        self._log(
            f"Validation complete: {len(valid_packages)} valid, {len(invalid_packages)} invalid"
        )
        if invalid_packages:
            self._log(
                f"Invalid packages skipped: {invalid_packages[:10]}{'...' if len(invalid_packages) > 10 else ''}"
            )

        return valid_packages

    def _is_root_filesystem_btrfs(self, plan):
        try:
            # Check manual partitions first
            manual_partitions = plan.get("manual_partitions", {})
            for device, assignment in manual_partitions.items():
                if assignment.get("mountpoint") == "/":
                    fs_type = assignment.get("format_fs", "")
                    self._log(f"Root filesystem from manual partitions: {fs_type}")
                    return fs_type == "btrfs"

            # Check auto layout
            auto_layout = plan.get("auto_layout", {})
            if auto_layout:
                fs_type = auto_layout.get("filesystem", "")
                self._log(f"Root filesystem from auto layout: {fs_type}")
                return fs_type == "btrfs"

            self._log(
                "Could not determine root filesystem type, defaulting to non-btrfs"
            )
            return False

        except Exception as e:
            self._log(f"Error determining root filesystem type: {e}")
            return False

    def _xbps_install(self, plan):
        pkgs = ["base-system", "grub"] + plan.get("software", [])
        if plan.get("uefi"):
            pkgs.append("grub-x86_64-efi")

        # Add btrfs-specific packages if root filesystem is btrfs
        if self._is_root_filesystem_btrfs(plan):
            pkgs.extend(["grub-btrfs", "grub-btrfs-runit"])
            self._log("Btrfs root filesystem detected - adding grub-btrfs packages")
        else:
            self._log("Non-btrfs root filesystem - skipping grub-btrfs packages")

        all_pkgs = sorted(list(set(pkgs)))
        self._log(f"Requested packages ({len(all_pkgs)} total): {all_pkgs}")

        # Setup XBPS configuration first
        try:
            self._setup_xbps_config()
        except Exception as setup_err:
            self._log(f"XBPS setup failed: {setup_err}")
            raise

        # Sync repositories first (without -r flag to sync host)
        self._log("Synchronizing host repositories...")
        try:
            result = subprocess.run(
                ["xbps-install", "-S"], text=True, capture_output=True
            )
            if result.returncode != 0:
                self._log(f"Host sync failed: {result.stderr}")
            else:
                self._log("Host repository sync: OK")
        except Exception as host_sync_err:
            self._log(f"Host sync error: {host_sync_err}")

        # Now sync target repositories
        self._log("Synchronizing target repositories...")
        try:
            result = subprocess.run(
                ["xbps-install", "-S", "-r", self.target_root],
                text=True,
                capture_output=True,
            )
            if result.stdout:
                self._log(f"Target sync STDOUT: {result.stdout}")
            if result.stderr:
                self._log(f"Target sync STDERR: {result.stderr}")
            if result.returncode != 0:
                self._log(f"Target sync failed with return code: {result.returncode}")
                raise subprocess.CalledProcessError(result.returncode, result.args)
            self._log("Target repository sync: OK")

        except subprocess.CalledProcessError as e:
            self._log(f"Repository sync failed with exit code {e.returncode}")
            raise

        # Validate packages before installation
        final_pkgs = self._validate_packages(all_pkgs)

        if not final_pkgs:
            self._log("No valid packages to install!")
            raise Exception("No valid packages found after validation")

        # If too many packages failed validation, fall back to minimal set
        if len(final_pkgs) < len(all_pkgs) * 0.7:  # Less than 70% success rate
            self._log(
                f"Many packages failed validation ({len(all_pkgs) - len(final_pkgs)} failed)"
            )
            self._log("Falling back to minimal essential package set")
            minimal_pkgs = ["base-system", "grub"]
            if plan.get("uefi"):
                minimal_pkgs.append("grub-x86_64-efi")
            # Add some essential packages that are likely to exist
            minimal_pkgs.extend(["NetworkManager", "bash-completion", "curl", "git"])
            final_pkgs = minimal_pkgs
            self._log(f"Using minimal package set: {final_pkgs}")

        # Install packages
        self._log(f"Installing {len(final_pkgs)} validated packages...")
        try:
            # Use Popen for real-time output instead of run with capture_output
            process = subprocess.Popen(
                ["xbps-install", "-uy", "-r", self.target_root] + final_pkgs,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
            )

            # Read output line by line in real-time
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    self._log(output.strip())

            # Wait for process to complete and get return code
            return_code = process.poll()
            if return_code != 0:
                self._log(f"Package installation failed with exit code {return_code}")
                raise subprocess.CalledProcessError(return_code, process.args)
            self._log("Package installation: OK")

        except subprocess.CalledProcessError as e:
            self._log(f"Package installation failed with exit code {e.returncode}")
            raise

    def _configure_hostname(self, plan):
        hostname = plan.get("user", {}).get("hostname")
        if hostname:
            with open(os.path.join(self.target_root, "etc/hostname"), "w") as f:
                f.write(hostname + "\n")

    def _configure_locale_kbd(self, plan):
        # Configure locale and keyboard layout
        self._log("Konfiguriere Sprache und Tastatur...")

        # Set locale
        language = plan.get("language", "de_DE.UTF-8")

        # Generate locale by uncommenting it in libc-locales
        try:
            locales_file = os.path.join(self.target_root, "etc/default/libc-locales")
            if os.path.exists(locales_file):
                with open(locales_file, "r") as f:
                    content = f.read()

                pattern = r"#?\b" + re.escape(language) + r"\b"
                content = re.sub(pattern, language, content)

                with open(locales_file, "w") as f:
                    f.write(content)
                self._log(f"Locale {language} in libc-locales aktiviert")

                # Reconfigure glibc-locales to generate the locale
                self._enter_chroot_mounts()
                try:
                    self._run(["xbps-reconfigure", "-f", "glibc-locales"], chroot=True)
                    self._log(f"Locale {language} wurde generiert")
                finally:
                    self._leave_chroot_mounts()
        except Exception as e:
            self._log(f"Warnung: Konnte Locale nicht generieren: {e}")

        # Set locale in locale.conf
        try:
            with open(os.path.join(self.target_root, "etc/locale.conf"), "w") as f:
                f.write(f"LANG={language}\n")
            self._log(f"Sprache auf {language} gesetzt")
        except Exception as e:
            self._log(f"Warnung: Konnte Sprache nicht setzen: {e}")

        # Set keyboard layout for console and X11
        keyboard = plan.get("keyboard")

        # Map X11 keyboard layouts to console layouts where they differ
        console_keyboard_map = {
            "de": "de",
            "de-nodeadkeys": "de-latin1-nodeadkeys",
            "fr": "fr",
            "es": "es",
            "it": "it",
            "gb": "gb",
            "us": "us",
        }

        console_keyboard = console_keyboard_map.get(keyboard, keyboard)

        # Update /etc/rc.conf for console keyboard layout
        rc_conf_path = os.path.join(self.target_root, "etc/rc.conf")
        try:
            # Read existing rc.conf or create a new one
            if os.path.exists(rc_conf_path):
                with open(rc_conf_path, "r") as f:
                    lines = f.readlines()
            else:
                lines = []

            # Look for KEYMAP line and update it, or add it if not found
            keymap_found = False
            with open(rc_conf_path, "w") as f:
                for line in lines:
                    if line.strip().startswith("KEYMAP="):
                        f.write(f"KEYMAP={console_keyboard}\n")
                        keymap_found = True
                    else:
                        f.write(line)

                # If KEYMAP was not found in the file, append it
                if not keymap_found:
                    f.write(f"KEYMAP={console_keyboard}\n")

            self._log(
                f"Konsolen-Tastaturlayout in rc.conf auf {console_keyboard} gesetzt"
            )
        except Exception as e:
            self._log(f"Warnung: Konnte rc.conf nicht aktualisieren: {e}")

        # Configure X11 keyboard layout
        if keyboard:
            self._configure_x11_keyboard(keyboard)

    def _configure_x11_keyboard(self, keyboard):
        # Configure X11 keyboard layout
        try:
            # Create X11 keyboard configuration
            x11_config_dir = os.path.join(self.target_root, "etc/X11/xorg.conf.d")
            os.makedirs(x11_config_dir, exist_ok=True)

            # Split keyboard layout and variant (e.g., "de-nodeadkeys" -> layout="de", variant="nodeadkeys")
            layout_parts = keyboard.split("-", 1)
            if len(layout_parts) > 1:
                layout = layout_parts[0]
                variant = layout_parts[1]
            else:
                layout = keyboard
                variant = None

            # Write keyboard configuration for X11
            with open(os.path.join(x11_config_dir, "00-keyboard.conf"), "w") as f:
                if variant:
                    f.write(
                        f"""Section "InputClass"
        Identifier "system-keyboard"
        MatchIsKeyboard "on"
        Option "XkbLayout" "{layout}"
        Option "XkbVariant" "{variant}"
        Option "XkbModel" "pc105"
EndSection
"""
                    )
                else:
                    f.write(
                        f"""Section "InputClass"
        Identifier "system-keyboard"
        MatchIsKeyboard "on"
        Option "XkbLayout" "{layout}"
        Option "XkbModel" "pc105"
EndSection
"""
                    )
                self._log(
                    f"X11-Tastaturlayout auf {layout}{'-' + variant if variant else ''} konfiguriert"
                )

        except Exception as e:
            self._log(
                f"⚠ Warnung: X11-Tastaturlayout-Konfiguration fehlgeschlagen: {e}"
            )

    def _configure_timezone(self, plan):
        # Configure system timezone
        self._log("Konfiguriere Zeitzone...")

        # Get timezone from plan, default to UTC if not specified
        timezone = plan.get("timezone", "UTC")
        if not timezone:
            timezone = "UTC"
            self._log("Keine Zeitzone angegeben, verwende UTC als Standard")

        self._log(f"Setze Zeitzone auf {timezone}")

        # Link the timezone file to /etc/localtime using ln -sf command
        source_tz_path = f"/usr/share/zoneinfo/{timezone}"
        target_localtime_path = os.path.join(self.target_root, "etc/localtime")

        # Check if timezone file exists first
        if not os.path.exists(
            os.path.join(self.target_root, source_tz_path.lstrip("/"))
        ):
            self._log(f"Warnung: Zeitzone {timezone} nicht gefunden, verwende UTC")
            source_tz_path = "/usr/share/zoneinfo/UTC"

        # Use the ln command to create the symlink
        try:
            self._run(["ln", "-sf", source_tz_path, target_localtime_path])
            self._log(
                f"Zeitzone erfolgreich gesetzt: {target_localtime_path} -> {source_tz_path}"
            )
        except Exception as e:
            self._log(f"Fehler beim Setzen der Zeitzone: {e}")

    def _configure_user(self, plan):
        # Configure user account
        user_config = plan.get("user", {})
        if not user_config:
            self._log("Keine Benutzerkonfiguration gefunden, überspringe...")
            return

        username = user_config.get("name") or user_config.get("username")
        password = user_config.get("password")
        root_password = user_config.get(
            "root_password", password
        )  # Use same password for root if not specified
        groups = user_config.get("groups", ["wheel"])

        self._log(f"Konfiguriere Benutzer: {username if username else 'nur root'}")
        self._enter_chroot_mounts()
        try:
            # Set root password first
            if root_password:
                self._log("Setze root-Passwort...")
                try:
                    process = subprocess.Popen(
                        ["chroot", self.target_root, "passwd", "root"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    stdout, stderr = process.communicate(
                        input=f"{root_password}\n{root_password}\n"
                    )
                    if process.returncode == 0:
                        self._log("✓ Root-Passwort erfolgreich gesetzt")
                    else:
                        self._log(
                            f"⚠ Warnung: Konnte root-Passwort nicht setzen: {stderr}"
                        )
                except Exception as e:
                    self._log(f"Fehler beim Setzen des root-Passworts: {e}")

            # Create regular user if specified
            if username:
                self._log(f"Erstelle Benutzer: {username}")
                try:
                    # Create common system groups that might be missing
                    self._log("Erstelle wichtige Benutzergruppen...")
                    user_groups = user_config.get("groups")

                    self._log("Prüfe verfügbare Benutzergruppen...")
                    for group in user_groups:
                        try:
                            # Check if group exists
                            result = self._run(
                                ["getent", "group", group],
                                chroot=True,
                                capture=True,
                                check=False,
                            )
                            if result.returncode == 0:
                                self._log(
                                    f"✓ Benutzergruppe '{group}' existiert bereits."
                                )
                            else:
                                self._log(
                                    f"⚠ Benutzergruppe '{group}' wird erstellt..."
                                )
                                result = self._run(
                                    ["groupadd", group], chroot=True, check=False
                                )
                        except:
                            self._log(
                                f"⚠ Konnte Benutzergruppe '{group}' nicht prüfen, überspringe..."
                            )

                    # Create user with home directory and shell
                    self._run(
                        [
                            "useradd",
                            "-m",
                            "-s",
                            "/bin/bash",
                            "-G",
                            ",".join(user_groups),
                            username,
                        ],
                        chroot=True,
                    )
                    self._log(
                        f"✓ Benutzer {username} erstellt (Gruppen: {','.join(user_groups)})"
                    )

                    # Set user password if provided
                    if password:
                        process = subprocess.Popen(
                            ["chroot", self.target_root, "passwd", username],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )
                        stdout, stderr = process.communicate(
                            input=f"{password}\n{password}\n"
                        )
                        if process.returncode == 0:
                            self._log(f"✓ Passwort für {username} gesetzt")
                        else:
                            self._log(
                                f"⚠ Warnung: Konnte Passwort für {username} nicht setzen: {stderr}"
                            )

                    # Configure sudofor wheel group
                    self._log("Konfiguriere sudo für wheel-Gruppe...")

                    try:
                        sudoers_path = os.path.join(
                            self.target_root, "etc/sudoers.d/wheel"
                        )
                        os.makedirs(os.path.dirname(sudoers_path), exist_ok=True)
                        with open(sudoers_path, "w") as f:
                            f.write("%wheel ALL=(ALL:ALL) ALL\n")
                        os.chmod(sudoers_path, 0o440)
                        self._log("✓ Sudo für wheel-Gruppe aktiviert")
                    except Exception as sudo_err:
                        self._log(f"Sudo-Konfiguration fehlgeschlagen: {sudo_err}")

                    self._log(f"✓ Benutzer {username} erfolgreich konfiguriert")
                except subprocess.CalledProcessError as e:
                    self._log(f"Fehler beim Erstellen des Benutzers: {e}")
                except Exception as e:
                    self._log(f"Unerwarteter Fehler bei Benutzererstellung: {e}")
            else:
                self._log("Kein Benutzername angegeben, nur root konfiguriert")

        except Exception as e:
            self._log(f"Fehler bei der Benutzerkonfiguration: {e}")
        finally:
            self._leave_chroot_mounts()

    def _enable_services(self, plan):
        # Enable system services
        self._log("Aktiviere System-Services...")

        # Define essential services for Void Linux
        essential_services = ["dbus", "elogind"]

        # Network services (try in order of preference)
        network_services = ["NetworkManager", "dhcpcd", "wpa_supplicant"]

        # Time synchronization services
        time_services = ["chronyd", "ntpd"]

        # Desktop services
        desktop_services = ["lightdm", "polkitd"]

        self._enter_chroot_mounts()
        try:
            # Create runit default directory
            runit_default_dir = os.path.join(
                self.target_root, "etc/runit/runsvdir/default"
            )
            os.makedirs(runit_default_dir, exist_ok=True)
            self._log("✓ Runit-Verzeichnis erstellt: /etc/runit/runsvdir/default")

            # Enable essential services
            for service in essential_services:
                self._enable_runit_service(service)

            # Enable one network service (prefer NetworkManager for desktop)
            network_enabled = False
            preferred_network = set()

            for service in network_services:
                if self._enable_runit_service(service):
                    network_enabled = True
                    preferred_network.add(service)
                    break

            if not network_enabled:
                # Try remaining network services
                for service in network_services:
                    if service not in preferred_network:
                        if self._enable_runit_service(service):
                            network_enabled = True
                            break

            if not network_enabled:
                self._log("⚠ Warnung: Kein Netzwerk-Service konnte aktiviert werden")

            # Enable time service
            time_enabled = False
            for service in time_services:
                if self._enable_runit_service(service):
                    time_enabled = True
                    break

            # Enable desktop services
            for service in desktop_services:
                self._enable_runit_service(service)

        finally:
            self._leave_chroot_mounts()

    def _enable_runit_service(self, service):
        # Enable a runit service
        try:
            # Check if service exists
            service_path = f"/etc/sv/{service}"
            full_service_path = os.path.join(self.target_root, service_path.lstrip("/"))

            if not os.path.exists(full_service_path):
                self._log(
                    f"⚠ Service {service} nicht verfügbar (/etc/sv/{service} nicht gefunden)"
                )
                return False

            # Target symlink path
            target_link = f"/etc/runit/runsvdir/default/{service}"
            full_target_path = os.path.join(self.target_root, target_link.lstrip("/"))

            # Remove existing symlink if present
            if os.path.exists(full_target_path) or os.path.islink(full_target_path):
                self._run(["rm", "-f", target_link], chroot=True)

            # Create symlink
            self._run(["ln", "-s", service_path, target_link], chroot=True)

            # Verify symlink was created
            if os.path.exists(full_target_path):
                self._log(f"✓ Service {service} aktiviert")
                return True
            else:
                self._log(f"⚠ Symlink für {service} konnte nicht erstellt werden")
                return False

        except Exception as e:
            self._log(f"⚠ Fehler beim Aktivieren von Service {service}: {e}")
            return False

    def _configure_pipewire(self, plan):
        if "pipewire" not in plan.get("software", []):
            return
        self._log("Konfiguriere PipeWire als Standard-Audioserver...")
        self._enter_chroot_mounts()
        try:
            os.makedirs(
                os.path.join(self.target_root, "etc/alsa/conf.d"), exist_ok=True
            )
            self._run(
                [
                    "ln",
                    "-sf",
                    "/usr/share/alsa/alsa.conf.d/50-pipewire.conf",
                    "/etc/alsa/conf.d/",
                ],
                chroot=True,
            )
            self._run(
                [
                    "ln",
                    "-sf",
                    "/usr/share/alsa/alsa.conf.d/99-pipewire-default.conf",
                    "/etc/alsa/conf.d/",
                ],
                chroot=True,
            )
        finally:
            self._leave_chroot_mounts()

    def _configure_flatpak(self, plan):
        if "flatpak" not in plan.get("software", []):
            return
        self._log("Füge Flathub-Repository zu Flatpak hinzu...")
        self._enter_chroot_mounts()
        try:
            self._run(
                [
                    "flatpak",
                    "remote-add",
                    "--if-not-exists",
                    "flathub",
                    "https://dl.flathub.org/repo/flathub.flatpakrepo",
                ],
                chroot=True,
            )
        finally:
            self._leave_chroot_mounts()

    def _install_bootloader(self, plan):
        self._log("Installiere GRUB Bootloader...")
        self._enter_chroot_mounts()
        try:
            if plan.get("uefi"):
                self._run(
                    [
                        "grub-install",
                        "--target=x86_64-efi",
                        "--efi-directory=/boot/efi",
                        "--bootloader-id=Void",
                    ],
                    chroot=True,
                )
            else:
                self._run(
                    [
                        "grub-install",
                        "--target=i386-pc",
                        plan["device"],
                    ],
                    chroot=True,
                )
            self._run(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], chroot=True)
        finally:
            self._leave_chroot_mounts()

    def _copy_iso_customizations(self):
        # Copy the full live environment to the installed system
        try:
            self._log("Kopiere vollständige Live-Umgebung zum installierten System...")

            # Execute the tar copy operation
            tar_in = "--create --one-file-system --xattrs"

            self._log(
                "Zähle Dateien, bitte warten... (dies kann einige Sekunden dauern)"
            )
            # Count total files first
            count_cmd = f"tar {tar_in} -v -f /dev/null / 2>/dev/null | wc -l"
            count_result = subprocess.run(
                count_cmd, shell=True, capture_output=True, text=True
            )
            try:
                copy_total = int(count_result.stdout.strip())
                self._log(f"Dateien zum Kopieren: {copy_total}")
            except ValueError:
                copy_total = 0
                self._log("Konnte Dateianzahl nicht ermitteln")

            # Execute the actual copy with progress tracking
            self._log("Starte Live-Umgebungskopie... (dies kann einige Minuten dauern)")

            cmd = f"tar {tar_in} -f - / 2>/dev/null | tar --extract --xattrs --xattrs-include='*' --preserve-permissions -f - -C {self.target_root}"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self._log("✓ Vollständige Live-Umgebung erfolgreich kopiert")
            else:
                self._log(f"Fehler bei der Live-Umgebungskopie: {result.stderr}")
                raise Exception(
                    f"Kopie der Live-Umgebung fehlgeschlagen: {result.stderr}"
                )

            # Clean up after copy
            self._cleanup_live_copy()

        except Exception as e:
            self._log(f"Fehler beim Kopieren der vollständigen Live-Umgebung: {e}")
            raise

    def _cleanup_live_copy(self):
        # Clean up after full live copy
        try:
            self._log("Bereinige temporäre Daten nach Live-Umgebungskopie...")

            # Remove live-specific user
            live_user_result = subprocess.run(
                ["chroot", self.target_root, "getent", "passwd", "anon"],
                capture_output=True,
                text=True,
            )
            if live_user_result.returncode == 0:
                self._log("Lösche live-Benutzer...")
                subprocess.run(
                    ["chroot", self.target_root, "userdel", "-r", "anon"],
                    capture_output=True,
                    text=True,
                )

            # Remove live-specific files
            live_files_to_remove = [
                "/etc/motd",
                "/etc/issue",
                "/usr/sbin/void-installer",
                "/etc/sudoers.d/99-void-live",
                "/etc/xbps.d/00-repo-default.conf",
            ]

            for live_file in live_files_to_remove:
                try:
                    full_path = os.path.join(self.target_root, live_file.lstrip("/"))
                    if os.path.exists(full_path):
                        os.remove(full_path)
                        self._log(f"Gelöscht: {live_file}")
                except Exception as e:
                    self._log(f"Fehler beim Löschen von {live_file}: {e}")

            # Update getty args to remove live user autologin
            getty_conf_path = os.path.join(self.target_root, "etc/sv/agetty-tty1/conf")
            if os.path.exists(getty_conf_path):
                with open(getty_conf_path, "r") as f:
                    content = f.read()
                # Remove live user from getty args
                content = content.replace(" -a anon", "")
                content = content.replace("--noclear -a anon", "--noclear")
                with open(getty_conf_path, "w") as f:
                    f.write(content)
                self._log("Live-User-Autologin in getty entfernt")

            self._log("Bereinigung der Live-Umgebung abgeschlossen")
        except Exception as e:
            self._log(f"Fehler bei der Bereinigung nach Live-Kopie: {e}")
            # Don't raise here as this is just cleanup

    def _copy_include_root(self, include_root: str):
        # Copy files from include_root directory to the installed system
        try:
            self._log(
                f"Kopiere Include-Root von {include_root} nach {self.target_root}..."
            )

            # Verify source directory exists
            if not os.path.exists(include_root):
                self._log(
                    f"Warnung: Include-Root Verzeichnis {include_root} existiert nicht"
                )
                return

            if not os.path.isdir(include_root):
                self._log(f"Fehler: {include_root} ist kein Verzeichnis")
                return

            # Count files to copy for progress indication
            total_files = 0
            for root, dirs, files in os.walk(include_root):
                total_files += len(files)

            self._log(f"Found {total_files} files to copy from {include_root}")

            copied_files = 0

            self._log(
                f"Verwende shutil zum Kopieren von {include_root} nach {self.target_root}..."
            )

            # Walk through source directory and copy files
            for root, dirs, files in os.walk(include_root):
                # Calculate destination path
                include_root_clean = include_root.rstrip("/")
                target_root_clean = self.target_root.rstrip("/")

                # Debug logging for path replacement
                self._log(f"DEBUG: Original root: {root}")
                self._log(f"DEBUG: include_root_clean: {include_root_clean}")
                self._log(f"DEBUG: target_root_clean: {target_root_clean}")

                dest_root = root.replace(include_root_clean, target_root_clean, 1)

                # Debug logging for calculated destination
                self._log(f"DEBUG: Calculated dest_root: {dest_root}")

                # Create destination directories if they don't exist
                for dir_name in dirs:
                    src_dir = os.path.join(root, dir_name)
                    dest_dir = os.path.join(dest_root, dir_name)
                    os.makedirs(dest_dir, exist_ok=True)
                    self._log(f"Verzeichnis erstellt: {dest_dir}")

                # Copy files
                for file_name in files:
                    src_file = os.path.join(root, file_name)
                    dest_file = os.path.join(dest_root, file_name)
                    try:
                        shutil.copy2(src_file, dest_file)
                        copied_files += 1
                        if copied_files % 50 == 0:
                            self._log(f"{copied_files} Dateien kopiert...")
                        self._log(f"Kopiert: {src_file} -> {dest_file}")
                    except Exception as file_err:
                        self._log(f"Fehler beim Kopieren von {src_file}: {file_err}")
                        # Continue with other files even if one fails

            self._log(f"✓ Include-Root erfolgreich kopiert ({copied_files} Dateien)")

        except Exception as e:
            self._log(f"Fehler beim Kopieren des Include-Root: {e}")
            raise

    def _enter_chroot_mounts(self):
        # Mount EFI variables first for UEFI systems
        if os.path.exists("/sys/firmware/efi"):
            self._run(["modprobe", "efivarfs"], check=False)
            self._run(
                ["mount", "-t", "efivarfs", "efivarfs", "/sys/firmware/efi/efivars"],
                check=False,
            )

        for p in ["/dev", "/proc", "/sys"]:
            target_path = os.path.join(self.target_root, p.lstrip("/"))
            os.makedirs(target_path, exist_ok=True)
            self._run(["mount", "--bind", p, target_path])

        # Mount EFI variables in chroot for UEFI systems
        if os.path.exists("/sys/firmware/efi"):
            efivars_target = os.path.join(self.target_root, "sys/firmware/efi/efivars")
            os.makedirs(efivars_target, exist_ok=True)
            self._run(
                ["mount", "--bind", "/sys/firmware/efi/efivars", efivars_target],
                check=False,
            )

        # Copy DNS configuration for network connectivity in chroot
        try:
            resolv_source = "/etc/resolv.conf"
            resolv_target = os.path.join(self.target_root, "etc/resolv.conf")
            if os.path.exists(resolv_source):
                os.makedirs(os.path.dirname(resolv_target), exist_ok=True)

                shutil.copy2(resolv_source, resolv_target)
                self._log("DNS configuration copied to chroot")
        except Exception as e:
            self._log(f"Warning: Could not copy DNS config: {e}")

    def _leave_chroot_mounts(self):
        # Remove DNS configuration copy
        try:
            resolv_target = os.path.join(self.target_root, "etc/resolv.conf")
            if os.path.exists(resolv_target):
                os.remove(resolv_target)
        except Exception as e:
            self._log(f"Warning: Could not remove DNS config copy: {e}")

        # Unmount EFI variables from chroot first
        if os.path.exists("/sys/firmware/efi"):
            efivars_target = os.path.join(self.target_root, "sys/firmware/efi/efivars")
            if os.path.exists(efivars_target) and self._is_mounted(efivars_target):
                try:
                    self._run(["umount", efivars_target])
                except subprocess.CalledProcessError:
                    pass

        for p in ["/dev", "/proc", "/sys"]:
            target_path = os.path.join(self.target_root, p.lstrip("/"))
            if os.path.exists(target_path) and self._is_mounted(target_path):
                try:
                    self._run(["umount", "-R", target_path])
                except subprocess.CalledProcessError:
                    pass
