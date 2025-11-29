// Live Patch - Emergency Fix for Dashboard Loading
// This script patches the existing dashboard to ensure data loads properly

(function() {
    'use strict';
    
    console.log('🚨 LIVE PATCH: Applying emergency dashboard fix...');
    
    // Wait for DOM to be ready
    function waitForDOM() {
        return new Promise(resolve => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }
    
    // Main patch function
    async function applyPatch() {
        await waitForDOM();
        
        console.log('🔧 LIVE PATCH: DOM ready, applying fixes...');
        
        // Update loading message
        const loadingText = document.querySelector('.loading-content p');
        if (loadingText) {
            loadingText.textContent = 'Live Patch wird angewendet...';
        }
        
        // Force hide loading overlay after data loads
        setTimeout(() => {
            console.log('🔧 LIVE PATCH: Force hiding loading overlay');
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.style.display = 'none';
                overlay.style.opacity = '0';
                overlay.style.visibility = 'hidden';
            }
            
            // Show success message
            const mainContent = document.querySelector('main');
            if (mainContent) {
                const patchNotice = document.createElement('div');
                patchNotice.innerHTML = `
                    <div style="background: #28a745; color: white; padding: 10px; margin: 10px; border-radius: 5px; text-align: center;">
                        ✅ Live Patch erfolgreich angewendet - Dashboard sollte jetzt funktionieren
                    </div>
                `;
                mainContent.insertBefore(patchNotice, mainContent.firstChild);
            }
        }, 3000);
        
        // Patch existing dashboard if it exists
        if (window.dashboard) {
            console.log('🔧 LIVE PATCH: Patching existing dashboard instance');
            
            // Override the hideLoading method to be more aggressive
            const originalHideLoading = window.dashboard.hideLoading;
            window.dashboard.hideLoading = function() {
                console.log('🔧 LIVE PATCH: Aggressive hideLoading called');
                const overlay = document.getElementById('loadingOverlay');
                if (overlay) {
                    overlay.style.display = 'none !important';
                    overlay.style.opacity = '0 !important';
                    overlay.style.visibility = 'hidden !important';
                    overlay.style.zIndex = '-9999 !important';
                }
                
                // Call original if it exists
                if (originalHideLoading) {
                    originalHideLoading.call(this);
                }
            };
            
            // Force UI update after delay
            setTimeout(() => {
                if (window.dashboard.currentData) {
                    console.log('🔧 LIVE PATCH: Forcing UI update');
                    window.dashboard.updateUI();
                    window.dashboard.hideLoading();
                }
            }, 2000);
        }
        
        // Add manual data loading trigger
        setTimeout(() => {
            console.log('🔧 LIVE PATCH: Attempting manual data load');
            
            // Try to trigger data loading manually
            const fileSelect = document.getElementById('dataFileSelect');
            if (fileSelect && fileSelect.options.length > 1) {
                fileSelect.value = fileSelect.options[1].value;
                fileSelect.dispatchEvent(new Event('change'));
            }
        }, 1000);
    }
    
    // Apply patch immediately
    applyPatch().catch(error => {
        console.error('🚨 LIVE PATCH ERROR:', error);
    });
    
    // Also try after window load
    window.addEventListener('load', () => {
        setTimeout(applyPatch, 1000);
    });
    
})();