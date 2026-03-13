#!/usr/bin/env python3
"""
DROID-NIKTO - Web Server Roaster with Attitude
ULTIMATE 2026 EDITION: Finding your misconfigurations since forever

"Your web server isn't just vulnerable. It's EMBARRASSING."
"Apache 1.3? That's not a server, that's a museum piece."

NOW WITH AUTO-INSTALL! One command. Everything works. You're welcome.
"""

import os
import sys
import re
import subprocess
import json
import time
import random
import select
import termios
import tty
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import socket
import urllib.request
import urllib.error

# ============================================================================
# TERMINAL COLORS (EDUCATIONAL BUT SPICY)
# ============================================================================

class Color:
    G = '\033[92m'  # Green - Success/Info
    R = '\033[91m'  # Red - Critical/Danger
    C = '\033[96m'  # Cyan - Headers/Important
    M = '\033[95m'  # Magenta - Highlights
    Y = '\033[93m'  # Yellow - Warnings/Fun
    B = '\033[94m'  # Blue - Neutral
    X = '\033[0m'   # Reset
    DIM = '\033[2m' # Dim - Secondary info

# ============================================================================
# TERMUX-OPTIMIZED DISPLAY (PERSISTENT HEADER + SCROLLABLE CONTENT)
# ============================================================================

class TermuxDisplay:
    """
    Fixed header display for narrow/mobile terminals.
    Header stays visible, content scrolls below.
    """

    def __init__(self):
        self.header_lines = []
        self.content_buffer = []
        self.max_content_lines = 50  # Prevent memory bloat
        self.term_width = self._get_term_width()
        self.is_termux = self._detect_termux()

    def _get_term_width(self):
        """Get terminal width, default to 40 for safety"""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except:
            return 40

    def _detect_termux(self):
        """Detect if running in Termux environment"""
        return 'TERMUX_VERSION' in os.environ or '/data/data/com.termux' in sys.executable

    def set_target(self, host: str, options: dict = None):
        """Set the persistent header with target info"""
        width = min(self.term_width, 50)  # Cap width for readability

        # Simple, clean header - no boxes that break
        self.header_lines = [
            f"{Color.C}{'━' * width}{Color.X}",
            f"{Color.Y}  🔥 DROID-NIKTO 2026{Color.X} {Color.DIM}|{Color.X} {Color.C}Web Security Scanner{Color.X}",
            f"{Color.C}{'━' * width}{Color.X}",
            f"{Color.G}  Target:{Color.X} {host}",
        ]

        if options:
            if options.get('port'):
                self.header_lines.append(f"{Color.G}  Ports:{Color.X} {options['port']}")
            if options.get('tuning'):
                tech_names = {
                    '0': 'File Upload', '1': 'Log Files', '2': 'Default Files',
                    '3': 'Info Disclosure', '4': 'XSS/Injection', '5': 'Remote Files',
                    '6': 'DoS Tests', '7': 'Remote Files (Srv)', '8': 'Command Exec',
                    '9': 'SQL Injection', 'a': 'Auth Bypass', 'b': 'Software ID',
                    'c': 'Source Inclusion'
                }
                techs = [tech_names.get(t, t) for t in options['tuning'] if t != 'x']
                if len(techs) <= 2:
                    self.header_lines.append(f"{Color.G}  Focus:{Color.X} {', '.join(techs)}")
                else:
                    self.header_lines.append(f"{Color.G}  Focus:{Color.X} {len(techs)} techniques")

        self.header_lines.append(f"{Color.C}{'━' * width}{Color.X}")

    def clear_and_draw(self, status_msg: str = "", progress_pct: int = 0):
        """Clear screen, redraw header, show status"""
        # Clear screen (Termux-friendly)
        os.system('clear' if os.name != 'nt' else 'cls')

        # Draw header
        for line in self.header_lines:
            print(line)

        # Status line - simple, no boxes
        if status_msg:
            bar_width = min(20, self.term_width - 20)
            filled = int((progress_pct / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)

            print(f"\n{Color.Y}  Status:{Color.X} {status_msg}")
            print(f"  {Color.C}{bar}{Color.X} {Color.G}{progress_pct}%{Color.X}")
            print()

    def log_finding(self, finding: dict, show_roast: bool = True):
        """Log a finding with minimal formatting"""
        severity = finding.get('severity', 'info')
        path = finding.get('path', 'unknown')
        status = finding.get('status', '')
        roast = finding.get('roast', '') if show_roast else ''

        # Color by severity
        color = Color.R if severity == 'critical' else Color.Y if severity == 'high' else Color.C if severity == 'medium' else Color.DIM

        # Simple format: [SEVERITY] path (status)
        status_str = f" {Color.DIM}({status}){Color.X}" if status else ""
        print(f"{color}[{severity.upper()}]{Color.X} {path}{status_str}")

        # Educational roast (one line, concise)
        if roast:
            print(f"  ↳ {Color.Y}{roast}{Color.X}")

        # CVE info if present
        if finding.get('cve'):
            print(f"  ↳ {Color.R}CVE: {finding['cve']}{Color.X}")

    def log_info(self, message: str):
        """Simple info line"""
        print(f"{Color.DIM}  ℹ {message}{Color.X}")

    def log_success(self, message: str):
        """Success message"""
        print(f"{Color.G}  ✓ {message}{Color.X}")

    def log_warning(self, message: str):
        """Warning message"""
        print(f"{Color.Y}  ⚠ {message}{Color.X}")

    def log_error(self, message: str):
        """Error message"""
        print(f"{Color.R}  ✗ {message}{Color.X}")


# ============================================================================
# CURATED HUMOR DATABASE (EDUCATIONAL + FUN, NOT OVERWHELMING)
# ============================================================================

class EducationalRoasts:
    """
    Security education through humor.
    Explains WHY things are bad, not just that they are bad.
    """

    SCAN_START = [
        "🔍 Mapping the battlefield... every server tells a story (usually a tragedy)",
        "🌐 Connecting... hope they updated since 2020 (they didn't)",
        "🕷️ Crawling... looking for doors left unlocked (metaphorically and literally)",
    ]

    PROGRESS_QUIPS = [
        "📡 Probing ports... 80 is open (like your security policy)",
        "🔎 Checking for default files... /admin exists? Shocking.",
        "🛡️ Testing headers... Strict-Transport-Security is MIA",
        "🔐 Looking for exposed configs... .env files love public attention",
        "📁 Hunting backup files... database.sql.bak is not a good look",
        "💉 Testing input validation... your sanitizer is on vacation",
        "🎭 Checking for info disclosure... servers love oversharing",
    ]

    SERVER_ROASTS = {
        'apache': {
            'old': "Apache {version} - Released when flip phones were cool. Update?",
            'very_old': "Apache {version} - This version can vote. And drink. And get hacked.",
            'ancient': "Apache {version} - Archaeologists called, they want their server back.",
        },
        'nginx': {
            'old': "nginx {version} - Fast, but your update policy is slow.",
            'default': "nginx {version} - Good choice, but versions matter.",
        },
        'iis': {
            'old': "IIS {version} - Windows Server called, it wants security patches.",
            'ancient': "IIS {version} - Still running XP-era software? Bold.",
        }
    }

    VULN_EDUCATION = {
        'outdated': [
            "Old software is like expired milk - technically works, but risky",
            "This version has known exploits. Updates exist for a reason.",
            "Security patches: not just for Tuesdays, but every day.",
        ],
        'directory_listing': [
            "Directory listing ON = 'Free files here!' sign for hackers",
            "Index of / shows every file. Every. Single. One.",
            "Turn off autoindexing. Please. For everyone's sake.",
        ],
        'default_files': [
            "Default files are hacker cheat sheets. Remove them.",
            "/phpinfo.php shows server guts. Don't expose guts.",
            "Test files in production? That's what staging is for.",
        ],
        'xss': [
            "XSS: When you trust user input more than you should (never)",
            "Input validation: because users can't be trusted",
            "XSS lets attackers run code in browsers. Bad times.",
        ],
        'sql_injection': [
            "SQLi in 2026? Prepared statements exist. Use them.",
            "Your database is talking to strangers. Stop that.",
            "Little Bobby Tables says: sanitize your inputs",
        ],
        'backup_files': [
            "Backup files in web root? That's not backup, that's exposure",
            ".bak files contain secrets. Secrets belong in vaults, not URLs",
            "If it ends in .old, .bak, or .backup, it shouldn't be public",
        ],
        'admin_exposed': [
            "Admin panels need IP restrictions. And 2FA. And strong passwords.",
            "/admin with default creds? That's not security, that's decoration",
            "Admin interfaces: powerful tools need powerful protection",
        ],
        'info_disclosure': [
            "Information disclosure: helping hackers since forever",
            "Server headers shouldn't tell your life story",
            "Error messages are for logs, not for users (or hackers)",
        ]
    }

    STATUS_CODES = {
        200: "OK - File exists and is accessible (check if it should be)",
        301: "Moved - Redirects can hide or expose. Check the destination",
        302: "Found - Temporary redirect. Still worth investigating",
        401: "Unauthorized - Needs creds. Try defaults, then brute force (ethically)",
        403: "Forbidden - Exists but blocked. Often bypassable. Try harder.",
        404: "Not Found - Good! Unless it's a fake 404. Check the body.",
        500: "Server Error - Something broke. Might be exploitable.",
        502: "Bad Gateway - Backend issues. Information leakage possible.",
    }

    COMPLETION = [
        "🎓 Lesson complete. Your server has homework.",
        "📚 Scan done. Time to patch, update, and secure.",
        "✅ Assessment finished. The report card is... educational.",
        "🎯 Mission accomplished. Vulnerabilities found = learning opportunities.",
    ]

    @classmethod
    def get_server_roast(cls, server_type: str, version: str, age: str = 'old'):
        """Get educational roast about server version"""
        templates = cls.SERVER_ROASTS.get(server_type.lower(), {})
        template = templates.get(age, templates.get('old', "{version} - Check for updates"))
        return template.format(version=version)

    @classmethod
    def get_vuln_education(cls, vuln_type: str) -> str:
        """Get educational explanation of vulnerability"""
        options = cls.VULN_EDUCATION.get(vuln_type, cls.VULN_EDUCATION['info_disclosure'])
        return random.choice(options)


# ============================================================================
# VULNERABILITY DATABASE (UNCHANGED - TECHNICAL CORE)
# ============================================================================

class WebVulnDB:
    """Real vulnerability database for web servers and applications"""

    def __init__(self):
        self.server_vulns = {
            'apache': {
                '2.2': {
                    'eol': '2017-07',
                    'cves': ['CVE-2017-15710', 'CVE-2017-7679', 'CVE-2017-3167']
                },
                '2.4.10': {'eol': '2015-01', 'cves': ['CVE-2014-3581']},
                '2.4.18': {'eol': '2016-04', 'cves': ['CVE-2016-4979']},
                '2.4.25': {'eol': '2017-07', 'cves': ['CVE-2017-15710']},
                '2.4.38': {'eol': '2019-04', 'cves': ['CVE-2019-0211']},
                '2.4.41': {'eol': '2019-10', 'cves': ['CVE-2019-10082']},
                '2.4.46': {'eol': '2020-08', 'cves': ['CVE-2020-11984']},
            },
            'nginx': {
                '1.4': {'eol': '2014-04', 'cves': ['CVE-2014-0133']},
                '1.6': {'eol': '2015-04', 'cves': ['CVE-2015-1197']},
                '1.8': {'eol': '2016-04', 'cves': ['CVE-2016-0747']},
                '1.10': {'eol': '2017-04', 'cves': ['CVE-2017-7529']},
                '1.12': {'eol': '2018-04', 'cves': ['CVE-2017-7529']},
                '1.14': {'eol': '2019-04', 'cves': ['CVE-2018-16843']},
                '1.16': {'eol': '2020-04', 'cves': ['CVE-2019-20372']},
                '1.18': {'eol': '2021-04', 'cves': ['CVE-2021-23017']},
                '1.20': {'eol': '2022-04', 'cves': ['CVE-2022-41741']},
                '1.22': {'eol': '2023-05', 'cves': ['CVE-2023-44487']},
            },
            'iis': {
                '6.0': {'eol': '2015-07', 'cves': ['CVE-2015-1635', 'CVE-2017-7269']},
                '7.0': {'eol': '2015-07', 'cves': ['CVE-2015-1635']},
                '7.5': {'eol': '2015-07', 'cves': ['CVE-2015-1635']},
                '8.0': {'eol': '2019-01', 'cves': ['CVE-2015-1635']},
                '8.5': {'eol': '2019-01', 'cves': ['CVE-2015-1635']},
                '10.0': {'eol': '2025-10', 'cves': ['CVE-2022-21907']},
            }
        }

        self.sensitive_paths = {
            '/admin': {'risk': 'high', 'desc': 'Admin panel'},
            '/wp-admin': {'risk': 'high', 'desc': 'WordPress admin'},
            '/phpmyadmin': {'risk': 'critical', 'desc': 'Database management'},
            '/backup': {'risk': 'critical', 'desc': 'Backup files'},
            '/.git': {'risk': 'critical', 'desc': 'Source code repository'},
            '/.env': {'risk': 'critical', 'desc': 'Environment variables'},
            '/config.php': {'risk': 'high', 'desc': 'Configuration file'},
            '/phpinfo.php': {'risk': 'medium', 'desc': 'System information'},
            '/api': {'risk': 'high', 'desc': 'API endpoint'},
            '/swagger': {'risk': 'medium', 'desc': 'API documentation'},
        }

    def check_server_version(self, server_string: str) -> Dict:
        """Parse server header and check against vulnerability DB"""
        result = {
            'server': 'Unknown',
            'version': 'Unknown',
            'vulnerabilities': [],
            'eol': None,
            'roast': None,
            'age': 'current'
        }

        server_lower = server_string.lower()

        if 'apache' in server_lower:
            result['server'] = 'Apache'
            version_match = re.search(r'apache/([\d\.]+)', server_lower)
            if version_match:
                version = version_match.group(1)
                result['version'] = version
                major_minor = '.'.join(version.split('.')[:2])

                # Determine age and vulnerabilities
                for ver_range, data in self.server_vulns['apache'].items():
                    if major_minor.startswith(ver_range) or version.startswith(ver_range):
                        result['vulnerabilities'] = data['cves']
                        result['eol'] = data['eol']
                        break

                # Determine roast severity
                if major_minor.startswith('2.2'):
                    result['age'] = 'ancient'
                elif major_minor in ['2.4.10', '2.4.18', '2.4.25']:
                    result['age'] = 'very_old'
                elif major_minor in ['2.4.38', '2.4.41', '2.4.46']:
                    result['age'] = 'old'

                result['roast'] = EducationalRoasts.get_server_roast('apache', version, result['age'])

        elif 'nginx' in server_lower:
            result['server'] = 'nginx'
            version_match = re.search(r'nginx/([\d\.]+)', server_lower)
            if version_match:
                version = version_match.group(1)
                result['version'] = version
                major_minor = '.'.join(version.split('.')[:2])

                for ver_range, data in self.server_vulns['nginx'].items():
                    if major_minor.startswith(ver_range) or version.startswith(ver_range):
                        result['vulnerabilities'] = data['cves']
                        result['eol'] = data['eol']
                        result['age'] = 'old'
                        break

                result['roast'] = EducationalRoasts.get_server_roast('nginx', version, result['age'])

        elif 'iis' in server_lower or 'microsoft-iis' in server_lower:
            result['server'] = 'IIS'
            version_match = re.search(r'iis/([\d\.]+)|microsoft-iis/([\d\.]+)', server_lower)
            if version_match:
                version = version_match.group(1) or version_match.group(2)
                result['version'] = version

                for ver_range, data in self.server_vulns['iis'].items():
                    if version.startswith(ver_range):
                        result['vulnerabilities'] = data['cves']
                        result['eol'] = data['eol']
                        result['age'] = 'old' if version.startswith('6') else 'current'
                        break

                result['roast'] = EducationalRoasts.get_server_roast('iis', version, result['age'])

        return result


# ============================================================================
# TERMUX-OPTIMIZED SCANNER CORE
# ============================================================================

class NiktoCore:
    """Nikto wrapper with Termux-optimized display"""

    def __init__(self):
        self.output_dir = Path.home() / '.droid-nikto'
        self.output_dir.mkdir(exist_ok=True)
        self.display = TermuxDisplay()
        self.vuln_db = WebVulnDB()
        self.nikto_path = self.find_nikto()

    def find_nikto(self) -> Optional[Path]:
        """Find nikto installation"""
        try:
            result = subprocess.run(['nikto', '-Version'], capture_output=True, text=True)
            if result.returncode == 0:
                return Path('nikto')
        except:
            pass

        possible_paths = [
            Path.home() / 'nikto' / 'program' / 'nikto.pl',
            Path('/usr/bin/nikto'),
            Path('/usr/local/bin/nikto'),
            Path('/data/data/com.termux/files/usr/bin/nikto'),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def is_termux(self):
        """Detect Termux environment"""
        return 'TERMUX_VERSION' in os.environ

    def auto_install_nikto(self):
        """Auto-install with Termux detection"""
        self.display.log_warning("Nikto not found in PATH")
        print(f"\n{Color.Y}Auto-install available. This will:{Color.X}")
        print(f"  • Update package lists")
        print(f"  • Install git, perl, openssl")
        print(f"  • Clone Nikto from GitHub")
        print(f"  • Set up command alias")

        response = input(f"\n{Color.C}Proceed with installation? (y/n): {Color.X}").lower()

        if response not in ['y', 'yes', 'yeah', 'sure']:
            print(f"{Color.Y}Installation cancelled.{Color.X}")
            print(f"Manual install: git clone https://github.com/sullo/nikto.git")
            return False

        print(f"\n{Color.C}Starting installation...{Color.X}\n")

        # Use pkg for Termux, apt for others
        pkg_manager = 'pkg' if self.is_termux() else 'apt-get'

        steps = [
            (f"Updating packages...", [pkg_manager, 'update', '-y']),
            (f"Installing git...", [pkg_manager, 'install', 'git', '-y']),
            (f"Installing perl...", [pkg_manager, 'install', 'perl', '-y']),
            (f"Installing openssl...", [pkg_manager, 'install', 'openssl', '-y']),
        ]

        for desc, cmd in steps:
            print(f"{Color.Y}  → {desc}{Color.X}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"{Color.R}     Failed: {result.stderr[:100]}{Color.X}")
            except Exception as e:
                print(f"{Color.R}     Error: {e}{Color.X}")

        # Clone Nikto
        nikto_dir = Path.home() / 'nikto'
        if nikto_dir.exists():
            print(f"{Color.Y}  → Updating existing Nikto...{Color.X}")
            subprocess.run(['git', '-C', str(nikto_dir), 'pull'], capture_output=True)
        else:
            print(f"{Color.Y}  → Cloning Nikto...{Color.X}")
            subprocess.run(['git', 'clone', 'https://github.com/sullo/nikto.git', str(nikto_dir)],
                         capture_output=True)

        # Set permissions
        nikto_pl = nikto_dir / 'program' / 'nikto.pl'
        if nikto_pl.exists():
            nikto_pl.chmod(0o755)
            print(f"{Color.G}  ✓ Nikto installed at {nikto_pl}{Color.X}")

            # Create alias
            bashrc = Path.home() / '.bashrc'
            alias_cmd = f'alias nikto="perl {nikto_pl}"\n'

            if bashrc.exists():
                content = bashrc.read_text()
                if 'alias nikto=' not in content:
                    with open(bashrc, 'a') as f:
                        f.write(f'\n# Added by DROID-Nikto\n{alias_cmd}')
            else:
                with open(bashrc, 'w') as f:
                    f.write(f'# Added by DROID-Nikto\n{alias_cmd}')

            print(f"{Color.G}  ✓ Alias added to .bashrc{Color.X}")
            self.nikto_path = nikto_pl
            return True
        else:
            print(f"{Color.R}  ✗ Installation failed{Color.X}")
            return False

    def check_nikto(self, auto_install=True):
        """Check/install nikto"""
        if self.nikto_path:
            return True

        if auto_install:
            return self.auto_install_nikto()
        return False

    def build_command(self, host: str, **kwargs) -> List[str]:
        """Build nikto command"""
        if self.nikto_path and self.nikto_path != Path('nikto'):
            cmd = ['perl', str(self.nikto_path), '-h', host]
        else:
            cmd = ['nikto', '-h', host]

        if kwargs.get('port'):
            cmd.extend(['-port', str(kwargs['port'])])
        if kwargs.get('maxtime'):
            cmd.extend(['-maxtime', str(kwargs['maxtime'])])
        if kwargs.get('ssl'):
            cmd.append('-ssl')
        if kwargs.get('nossl'):
            cmd.append('-nossl')
        if kwargs.get('output'):
            cmd.extend(['-output', kwargs['output']])
        if kwargs.get('format'):
            cmd.extend(['-Format', kwargs['format']])
        if kwargs.get('useproxy'):
            cmd.extend(['-useproxy', kwargs['useproxy']])
        if kwargs.get('tuning'):
            cmd.extend(['-Tuning', kwargs['tuning']])

        return cmd

    def run_scan(self, host: str, **kwargs) -> Dict:
        """Run scan with Termux-optimized display"""
        if not self.check_nikto(auto_install=True):
            return {'error': 'Nikto not available', 'host': host}

        # Set up display
        self.display.set_target(host, kwargs)

        cmd = self.build_command(host, **kwargs)
        self.display.log_info(f"Command: {' '.join(cmd[-4:])}...")  # Show last part only

        # Initial draw
        self.display.clear_and_draw(random.choice(EducationalRoasts.SCAN_START), 0)

        findings = []
        server_info = {}
        progress = 0
        last_update = time.time()

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            output_buffer = []

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    output_buffer.append(line)

                    # Update progress every 2 seconds or on significant events
                    current_time = time.time()
                    if current_time - last_update > 2:
                        progress = min(progress + 5, 95)
                        quip = random.choice(EducationalRoasts.PROGRESS_QUIPS)
                        self.display.clear_and_draw(quip, progress)
                        last_update = current_time

                    # Parse important lines
                    if '+ Server:' in line:
                        match = re.search(r'\+ Server: (.+)', line)
                        if match:
                            server_str = match.group(1).strip()
                            server_info = self.vuln_db.check_server_version(server_str)
                            self.display.log_success(f"Detected: {server_str}")
                            if server_info.get('roast'):
                                print(f"    {Color.Y}{server_info['roast']}{Color.X}")

                    elif line.startswith('+ /') and '200' in line:
                        path_match = re.search(r'\+ (/[^ :]+)', line)
                        if path_match:
                            path = path_match.group(1)
                            finding = {
                                'path': path,
                                'status': 200,
                                'severity': 'info',
                                'roast': ''
                            }

                            # Check against sensitive paths
                            if path in self.vuln_db.sensitive_paths:
                                info = self.vuln_db.sensitive_paths[path]
                                finding['severity'] = info['risk']
                                finding['description'] = info['desc']

                                # Educational roast
                                if 'admin' in path:
                                    finding['roast'] = EducationalRoasts.get_vuln_education('admin_exposed')
                                elif 'backup' in path:
                                    finding['roast'] = EducationalRoasts.get_vuln_education('backup_files')
                                elif 'phpmyadmin' in path:
                                    finding['roast'] = "Database admin exposed. Use VPN + strong passwords."

                            findings.append(finding)
                            self.display.log_finding(finding)

                    elif 'OSVDB' in line or 'CVE' in line:
                        cve_match = re.search(r'(CVE-\d{4}-\d+)', line)
                        finding = {
                            'path': 'Vulnerability detected',
                            'severity': 'high',
                            'cve': cve_match.group(1) if cve_match else None,
                            'roast': EducationalRoasts.get_vuln_education('outdated')
                        }
                        findings.append(finding)
                        self.display.log_finding(finding)

            # Final update
            self.display.clear_and_draw(random.choice(EducationalRoasts.COMPLETION), 100)

            return {
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'server': server_info,
                'findings': findings,
                'total_findings': len(findings)
            }

        except KeyboardInterrupt:
            self.display.log_warning("Scan interrupted by user")
            return {'error': 'Interrupted', 'host': host}
        except Exception as e:
            self.display.log_error(f"Scan failed: {e}")
            return {'error': str(e), 'host': host}

    def generate_report(self, results: Dict):
        """Generate final report"""
        print(f"\n{Color.C}{'━' * 40}{Color.X}")
        print(f"{Color.Y}  SCAN SUMMARY{Color.X}")
        print(f"{Color.C}{'━' * 40}{Color.X}\n")

        if results.get('server'):
            srv = results['server']
            print(f"{Color.G}Server:{Color.X} {srv.get('server', 'Unknown')} {srv.get('version', '')}")
            if srv.get('eol'):
                print(f"{Color.Y}End of Life:{Color.X} {srv['eol']}")
            if srv.get('vulnerabilities'):
                print(f"{Color.R}Known CVEs:{Color.X} {len(srv['vulnerabilities'])}")
                for cve in srv['vulnerabilities'][:3]:
                    print(f"  • {cve}")

        # Count findings by severity
        critical = len([f for f in results.get('findings', []) if f.get('severity') == 'critical'])
        high = len([f for f in results.get('findings', []) if f.get('severity') == 'high'])
        medium = len([f for f in results.get('findings', []) if f.get('severity') == 'medium'])

        print(f"\n{Color.G}Findings:{Color.X}")
        if critical:
            print(f"  {Color.R}💀 Critical: {critical}{Color.X}")
        if high:
            print(f"  {Color.R}🔥 High: {high}{Color.X}")
        if medium:
            print(f"  {Color.Y}⚠️  Medium: {medium}{Color.X}")

        print(f"\n{Color.C}{random.choice(EducationalRoasts.COMPLETION)}{Color.X}")
        print(f"{Color.DIM}Report saved: {self.output_dir}{Color.X}")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

class DroidNikto:
    """Main controller"""

    def __init__(self):
        self.core = NiktoCore()

    def run(self, args):
        """Execute scan"""
        # Show banner (once, at start)
        print(f"\n{Color.C}DROID-NIKTO 2026{Color.X} {Color.DIM}|{Color.X} {Color.Y}Educational Web Security Scanner{Color.X}\n")

        if args.update:
            print("Updating Nikto...")
            subprocess.run(['nikto', '-update'])
            return

        host = args.host
        kwargs = {}

        if args.port:
            kwargs['port'] = args.port
        if args.ssl:
            kwargs['ssl'] = True
        if args.nossl:
            kwargs['nossl'] = True
        if args.tuning:
            kwargs['tuning'] = args.tuning
        if args.output:
            kwargs['output'] = args.output
        if args.format:
            kwargs['format'] = args.format

        results = self.core.run_scan(host, **kwargs)

        if 'error' not in results:
            self.core.generate_report(results)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='DROID-NIKTO - Educational Web Security Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  droid-nikto.py -t example.com              Basic scan
  droid-nikto.py -t example.com -port 8080   Specific port
  droid-nikto.py -t example.com -tuning 49   SQLi + Command exec only
  droid-nikto.py -t example.com -ssl         Force SSL
        """
    )

    parser.add_argument('-t', '--host', required=True, help='Target host')
    parser.add_argument('-port', help='Port(s) to scan')
    parser.add_argument('-ssl', action='store_true', help='Force SSL')
    parser.add_argument('-nossl', action='store_true', help='Disable SSL')
    parser.add_argument('-tuning', help='Scan techniques (0-9,a-c,x)')
    parser.add_argument('-output', help='Output file')
    parser.add_argument('-format', choices=['csv', 'html', 'txt', 'xml'])
    parser.add_argument('--update', action='store_true', help='Update Nikto')

    args = parser.parse_args()

    droid = DroidNikto()
    droid.run(args)


if __name__ == "__main__":
    main()
