// Minimal test for dashboard data loading
console.log('🧪 Starting minimal dashboard test...');

async function testMinimalDataLoading() {
    try {
        console.log('📁 Testing file list access...');
        const fileResponse = await fetch('./data/file_list.json');
        console.log('File list response:', fileResponse.status, fileResponse.statusText);
        
        if (fileResponse.ok) {
            const files = await fileResponse.json();
            console.log('✅ Files found:', files);
            
            if (files.length > 0) {
                const firstFile = files[0];
                console.log(`📊 Testing first file: ${firstFile}`);
                
                const dataResponse = await fetch(`./data/${encodeURIComponent(firstFile)}`);
                console.log('Data file response:', dataResponse.status, dataResponse.statusText);
                
                if (dataResponse.ok) {
                    const data = await dataResponse.json();
                    console.log('✅ Data loaded successfully:', {
                        keys: Object.keys(data),
                        positiveCount: data.positive?.length || 0,
                        negativeCount: data.negative?.length || 0,
                        combinedCount: data.combined?.length || 0
                    });
                    
                    // Test UI element access
                    console.log('🔍 Testing UI element access...');
                    const elements = [
                        'totalPlayersDisplay',
                        'totalAlliancesDisplay', 
                        'updateStatus',
                        'totalScore',
                        'avgScore',
                        'highestScore',
                        'activeGames',
                        'topPlayersList',
                        'allianceRanking',
                        'lastUpdate',
                        'loadingOverlay'
                    ];
                    
                    elements.forEach(id => {
                        const element = document.getElementById(id);
                        console.log(`Element ${id}:`, element ? '✅ Found' : '❌ Missing');
                    });
                    
                } else {
                    console.error('❌ Failed to load data file');
                }
            }
        } else {
            console.error('❌ Failed to load file list');
        }
    } catch (error) {
        console.error('❌ Test error:', error);
    }
}

// Run test immediately
testMinimalDataLoading();