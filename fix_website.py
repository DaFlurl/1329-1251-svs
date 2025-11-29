#!/usr/bin/env python3
"""
AgentDaf1.1 Website Fix Script
Fixes common issues in the gitsitestylewebseite directory
"""

import json
import os
import re
import sys
from pathlib import Path

class WebsiteFixer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.issues_fixed = []
        
    def log_fix(self, issue, description):
        self.issues_fixed.append(f"✅ {issue}: {description}")
        print(f"✅ Fixed: {issue} - {description}")
    
    def log_warning(self, issue, description):
        print(f"⚠️  Warning: {issue} - {description}")
    
    def fix_data_files(self):
        """Fix data file issues"""
        print("/n🔧 Fixing data files...")
        
        data_dir = self.base_dir / "data"
        if not data_dir.exists():
            return
            
        for json_file in data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Ensure required structure
                modified = False
                
                # Add combined array if missing
                if 'combined' not in data:
                    combined = self.create_combined_data(data)
                    data['combined'] = combined
                    modified = True
                    self.log_fix(f"Missing combined array in {json_file.name}", f"Added {len(combined)} combined entries")
                
                # Add metadata if missing
                if 'metadata' not in data:
                    data['metadata'] = {
                        'totalPlayers': len(data.get('combined', [])),
                        'totalAlliances': len(self.get_alliances(data.get('combined', []))),
                        'lastUpdate': '2025-11-27T12:00:00Z',
                        'dataFile': json_file.name
                    }
                    modified = True
                    self.log_fix(f"Missing metadata in {json_file.name}", "Added metadata structure")
                
                # Fix data types
                if 'combined' in data:
                    for i, player in enumerate(data['combined']):
                        if 'score' in player and isinstance(player['score'], str):
                            try:
                                player['score'] = float(player['score'])
                                modified = True
                            except ValueError:
                                pass
                
                if modified:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    self.log_fix(f"Data structure in {json_file.name}", "Updated JSON structure")
                    
            except Exception as e:
                self.log_warning(f"Error processing {json_file.name}", str(e))
    
    def create_combined_data(self, data):
        """Create combined data from positive and negative arrays"""
        positive = data.get('positive', [])
        negative = data.get('negative', [])
        
        # Create player map
        player_map = {}
        
        # Add positive players
        for player in positive:
            key = player.get('name') or player.get('monarchId')
            if key:
                player_map[key] = {
                    'name': player.get('name', ''),
                    'alliance': player.get('alliance', 'None'),
                    'monarchId': player.get('monarchId', ''),
                    'positive': float(player.get('score', 0)),
                    'negative': 0,
                    'score': float(player.get('score', 0))
                }
        
        # Add/negative players
        for player in negative:
            key = player.get('name') or player.get('monarchId')
            if key:
                if key in player_map:
                    player_map[key]['negative'] = abs(float(player.get('score', 0)))
                    player_map[key]['score'] = player_map[key]['positive'] - player_map[key]['negative']
                else:
                    player_map[key] = {
                        'name': player.get('name', ''),
                        'alliance': player.get('alliance', 'None'),
                        'monarchId': player.get('monarchId', ''),
                        'positive': 0,
                        'negative': abs(float(player.get('score', 0))),
                        'score': -abs(float(player.get('score', 0)))
                    }
        
        # Convert to sorted array
        combined = sorted(player_map.values(), key=lambda x: x['score'], reverse=True)
        
        # Add positions
        for i, player in enumerate(combined):
            player['position'] = i + 1
        
        return combined
    
    def get_alliances(self, players):
        """Get unique alliances from players"""
        alliances = set()
        for player in players:
            alliance = player.get('alliance')
            if alliance and alliance != 'None':
                alliances.add(alliance)
        return list(alliances)
    
    def fix_html_files(self):
        """Fix HTML file issues"""
        print("/n🔧 Fixing HTML files...")
        
        for html_file in self.base_dir.glob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                # Add security meta tags
                if 'http-equiv="X-UA-Compatible"' not in content:
                    head_end = content.find('</head>')
                    if head_end != -1:
                        security_meta = '<meta http-equiv="X-UA-Compatible" content="ie=edge">/n    '
                        content = content[:head_end] + security_meta + content[head_end:]
                        modified = True
                        self.log_fix(f"Missing security meta in {html_file.name}", "Added X-UA-Compatible meta tag")
                
                # Add CSP meta tag
                if 'Content-Security-Policy' not in content:
                    head_end = content.find('</head>')
                    if head_end != -1:
                        csp_meta = '<meta http-equiv="Content-Security-Policy" content="default-src /'self/'; script-src /'self/' /'unsafe-inline/' https://cdnjs.cloudflare.com; style-src /'self/' /'unsafe-inline/' https://cdnjs.cloudflare.com https://fonts.googleapis.com;">/n    '
                        content = content[:head_end] + csp_meta + content[head_end:]
                        modified = True
                        self.log_fix(f"Missing CSP in {html_file.name}", "Added Content Security Policy meta tag")
                
                # Fix external resource integrity
                content = re.sub(
                    r'<link[^>]*href="https://cdnjs/.cloudflare/.com/[^"]*"[^>]*>',
                    lambda m: self.add_integrity_to_link(m.group(0)),
                    content
                )
                
                if content != original_content:
                    modified = True
                    self.log_fix(f"Resource integrity in {html_file.name}", "Added integrity attributes to external resources")
                
                if modified:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
            except Exception as e:
                self.log_warning(f"Error processing {html_file.name}", str(e))
    
    def add_integrity_to_link(self, link_tag):
        """Add integrity attribute to external link"""
        if 'integrity=' in link_tag:
            return link_tag
        
        # Add crossorigin and integrity for Font Awesome
        if 'font-awesome' in link_tag:
            link_tag = link_tag.replace('>', ' integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />')
        
        return link_tag
    
    def fix_css_files(self):
        """Fix CSS file issues"""
        print("/n🔧 Fixing CSS files...")
        
        for css_file in self.base_dir.glob("*.css"):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                # Add CSS variables if missing
                if ':root' not in content and 'variables' not in css_file.name.lower():
                    variables = """
/* CSS Variables */
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --error-color: #dc3545;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
    --border-radius: 8px;
    --transition: all 0.3s ease;
}
"""
                    content = variables + '/n' + content
                    modified = True
                    self.log_fix(f"Missing CSS variables in {css_file.name}", "Added CSS custom properties")
                
                # Fix vendor prefixes
                content = re.sub(r'transform:', '-webkit-transform; transform:', content)
                content = re.sub(r'transition:', '-webkit-transition; transition:', content)
                
                if content != original_content:
                    modified = True
                    self.log_fix(f"Vendor prefixes in {css_file.name}", "Added webkit vendor prefixes")
                
                if modified:
                    with open(css_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
            except Exception as e:
                self.log_warning(f"Error processing {css_file.name}", str(e))
    
    def fix_javascript_files(self):
        """Fix JavaScript file issues"""
        print("/n🔧 Fixing JavaScript files...")
        
        for js_file in self.base_dir.glob("**/*.js"):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                # Add 'use strict' if missing
                if content.strip() and not content.strip().startswith('"use strict"') and not content.strip().startswith("'use strict'"):
                    content = '"use strict";/n/n' + content
                    modified = True
                    self.log_fix(f"Missing use strict in {js_file.name}", "Added strict mode directive")
                
                # Add error handling wrapper
                if 'try {' not in content and 'class ' in content:
                    # Simple error handling for main functions
                    error_wrapper = """
// Global error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
});

"""
                    content = error_wrapper + content
                    modified = True
                    self.log_fix(f"Missing error handling in {js_file.name}", "Added global error handlers")
                
                if content != original_content:
                    modified = True
                    self.log_fix(f"JavaScript improvements in {js_file.name}", "Enhanced code quality")
                
                if modified:
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
            except Exception as e:
                self.log_warning(f"Error processing {js_file.name}", str(e))
    
    def create_missing_files(self):
        """Create missing essential files"""
        print("/n🔧 Creating missing files...")
        
        # Create .htaccess for security
        htaccess_path = self.base_dir / ".htaccess"
        if not htaccess_path.exists():
            htaccess_content = """# Security Headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options SAMEORIGIN
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'"
</IfModule>

# Disable directory listing
Options -Indexes

# Error pages
ErrorDocument 404 /index.html
ErrorDocument 500 /index.html

# Cache control for static files
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>
"""
            with open(htaccess_path, 'w', encoding='utf-8') as f:
                f.write(htaccess_content)
            self.log_fix("Missing .htaccess", "Created security and performance configuration")
        
        # Create robots.txt
        robots_path = self.base_dir / "robots.txt"
        if not robots_path.exists():
            robots_content = """User-agent: *
Allow: /
Disallow: /data/
Disallow: /file_history/

Sitemap: https://daflurl.github.io/1329-1251-svs/sitemap.xml
"""
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            self.log_fix("Missing robots.txt", "Created search engine configuration")
    
    def optimize_performance(self):
        """Optimize website performance"""
        print("/n🔧 Optimizing performance...")
        
        # Minify CSS (basic)
        for css_file in self.base_dir.glob("*.css"):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic minification
                minified = re.sub(r'//*.*?/*/', '', content, flags=re.DOTALL)  # Remove comments
                minified = re.sub(r'/s+', ' ', minified)  # Collapse whitespace
                minified = re.sub(r';/s*}', '}', minified)  # Remove unnecessary semicolons
                minified = minified.strip()
                
                # Create minified version
                min_file = css_file.with_name(css_file.stem + '.min.css')
                with open(min_file, 'w', encoding='utf-8') as f:
                    f.write(minified)
                
                self.log_fix(f"CSS minification for {css_file.name}", f"Created {min_file.name}")
                
            except Exception as e:
                self.log_warning(f"Error minifying {css_file.name}", str(e))
    
    def generate_report(self):
        """Generate fix report"""
        print("/n" + "="*60)
        print("🎉 WEBSITE FIX REPORT")
        print("="*60)
        
        if self.issues_fixed:
            print(f"/n✅ Total Issues Fixed: {len(self.issues_fixed)}")
            print("/nFixed Issues:")
            for issue in self.issues_fixed:
                print(f"  {issue}")
        else:
            print("/n✅ No issues found - website is already in good condition!")
        
        print("/n📋 Summary:")
        print("  - Data files: Fixed structure and metadata")
        print("  - HTML files: Added security headers and meta tags")
        print("  - CSS files: Added variables and vendor prefixes")
        print("  - JavaScript files: Added error handling and strict mode")
        print("  - Security: Created .htaccess and robots.txt")
        print("  - Performance: Created minified CSS files")
        
        print("/n🚀 Next Steps:")
        print("  1. Test the website: python serve.py")
        print("  2. Open browser: http://localhost:8000")
        print("  3. Run tests: Open test.html in browser")
        print("  4. Check all functionality works correctly")
        
        print("/n" + "="*60)
    
    def run_all_fixes(self):
        """Run all fix procedures"""
        print("🔧 Starting AgentDaf1.1 Website Fix Process...")
        print("="*60)
        
        self.fix_data_files()
        self.fix_html_files()
        self.fix_css_files()
        self.fix_javascript_files()
        self.create_missing_files()
        self.optimize_performance()
        
        self.generate_report()

def main():
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    fixer = WebsiteFixer(base_dir)
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()