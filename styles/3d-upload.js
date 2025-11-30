// 3D File Upload with Animated Effects
class Upload3D {
    constructor(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.files = [];
        this.isUploading = false;
        this.dragCounter = 0;
        
        this.init();
    }
    
    init() {
        this.createUploadHTML();
        this.setupEventListeners();
        this.initializeParticles();
    }
    
    createUploadHTML() {
        this.container.innerHTML = `
            <div class="upload-3d-area" id="uploadArea">
                <div class="upload-3d-particles" id="uploadParticles"></div>
                <div class="upload-3d-content">
                    <div class="upload-3d-icon">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                    </div>
                    <div class="upload-3d-text">Drop your Excel files here</div>
                    <div class="upload-3d-subtext">or click to browse (supports .xlsx, .xls, .csv)</div>
                    <button class="upload-3d-button" id="uploadButton">Choose Files</button>
                    <input type="file" id="fileInput" accept=".xlsx,.xls,.csv" multiple style="display: none;">
                </div>
                <div class="upload-3d-progress" id="uploadProgress">
                    <div class="upload-3d-progress-bar">
                        <div class="upload-3d-progress-fill" id="progressFill"></div>
                    </div>
                    <div class="upload-3d-progress-text" id="progressText">0%</div>
                </div>
                <div class="upload-3d-file-list" id="fileList"></div>
            </div>
        `;
        
        this.uploadArea = this.container.querySelector('#uploadArea');
        this.fileInput = this.container.querySelector('#fileInput');
        this.uploadButton = this.container.querySelector('#uploadButton');
        this.progressContainer = this.container.querySelector('#uploadProgress');
        this.progressFill = this.container.querySelector('#progressFill');
        this.progressText = this.container.querySelector('#progressText');
        this.fileList = this.container.querySelector('#fileList');
        this.particlesContainer = this.container.querySelector('#uploadParticles');
    }
    
    setupEventListeners() {
        // File input events
        this.uploadButton.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragenter', this.handleDragEnter.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    handleDragEnter(e) {
        e.preventDefault();
        this.dragCounter++;
        this.uploadArea.classList.add('dragover');
        this.createDragParticles();
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.dragCounter--;
        if (this.dragCounter === 0) {
            this.uploadArea.classList.remove('dragover');
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.dragCounter = 0;
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        this.handleFileSelect(files);
    }
    
    handleFileSelect(files) {
        const validFiles = Array.from(files).filter(file => 
            file.name.match(/\.(xlsx|xls|csv)$/i)
        );
        
        if (validFiles.length === 0) {
            this.showError('Please select valid Excel files (.xlsx, .xls, .csv)');
            return;
        }
        
        this.files = [...this.files, ...validFiles];
        this.updateFileList();
        this.createSuccessParticles();
        
        if (validFiles.length > 0) {
            this.simulateUpload();
        }
    }
    
    updateFileList() {
        this.fileList.innerHTML = '';
        
        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'upload-3d-file-item';
            fileItem.innerHTML = `
                <div class="upload-3d-file-icon">${this.getFileIcon(file.name)}</div>
                <div class="upload-3d-file-info">
                    <div class="upload-3d-file-name">${file.name}</div>
                    <div class="upload-3d-file-size">${this.formatFileSize(file.size)}</div>
                </div>
                <button class="upload-3d-file-remove" data-index="${index}">×</button>
            `;
            
            this.fileList.appendChild(fileItem);
            
            // Add remove event listener
            fileItem.querySelector('.upload-3d-file-remove').addEventListener('click', (e) => {
                this.removeFile(parseInt(e.target.dataset.index));
            });
        });
    }
    
    removeFile(index) {
        this.files.splice(index, 1);
        this.updateFileList();
        this.createRemoveParticles(index);
    }
    
    getFileIcon(filename) {
        if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) {
            return '📊';
        } else if (filename.endsWith('.csv')) {
            return '📋';
        }
        return '📄';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async simulateUpload() {
        if (this.isUploading) return;
        
        this.isUploading = true;
        this.uploadArea.classList.add('uploading');
        this.progressContainer.classList.add('active');
        
        let progress = 0;
        const increment = 100 / (this.files.length * 10); // 10 steps per file
        
        const uploadInterval = setInterval(() => {
            progress += increment;
            if (progress >= 100) {
                progress = 100;
                clearInterval(uploadInterval);
                this.completeUpload();
            }
            
            this.updateProgress(progress);
        }, 200);
    }
    
    updateProgress(progress) {
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `${Math.round(progress)}%`;
        
        // Add glow effect based on progress
        const intensity = progress / 100;
        this.progressFill.style.boxShadow = `0 0 ${20 + intensity * 30}px rgba(96, 165, 250, ${0.5 + intensity * 0.3})`;
    }
    
    completeUpload() {
        this.isUploading = false;
        this.uploadArea.classList.remove('uploading');
        this.uploadArea.classList.add('success');
        
        this.showSuccess('Files uploaded successfully!');
        this.createCompletionParticles();
        
        // Reset after delay
        setTimeout(() => {
            this.uploadArea.classList.remove('success');
            this.progressContainer.classList.remove('active');
            this.progressFill.style.width = '0%';
            this.progressText.textContent = '0%';
        }, 3000);
        
        // Trigger custom event
        this.container.dispatchEvent(new CustomEvent('uploadComplete', {
            detail: { files: this.files }
        }));
    }
    
    showError(message) {
        this.uploadArea.classList.add('error');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'upload-3d-error-message';
        errorElement.textContent = message;
        this.uploadArea.appendChild(errorElement);
        
        this.createErrorParticles();
        
        setTimeout(() => {
            this.uploadArea.classList.remove('error');
            errorElement.remove();
        }, 3000);
    }
    
    showSuccess(message) {
        const successElement = document.createElement('div');
        successElement.className = 'upload-3d-success-message';
        successElement.textContent = message;
        this.uploadArea.appendChild(successElement);
        
        setTimeout(() => {
            successElement.remove();
        }, 3000);
    }
    
    initializeParticles() {
        this.particles = [];
    }
    
    createDragParticles() {
        for (let i = 0; i < 10; i++) {
            setTimeout(() => {
                this.createParticle('drag');
            }, i * 50);
        }
    }
    
    createSuccessParticles() {
        for (let i = 0; i < 15; i++) {
            setTimeout(() => {
                this.createParticle('success');
            }, i * 30);
        }
    }
    
    createErrorParticles() {
        for (let i = 0; i < 8; i++) {
            setTimeout(() => {
                this.createParticle('error');
            }, i * 40);
        }
    }
    
    createRemoveParticles(index) {
        const fileItems = this.fileList.querySelectorAll('.upload-3d-file-item');
        const targetItem = fileItems[index];
        
        if (targetItem) {
            const rect = targetItem.getBoundingClientRect();
            const containerRect = this.particlesContainer.getBoundingClientRect();
            
            for (let i = 0; i < 6; i++) {
                this.createParticle('remove', {
                    x: rect.left - containerRect.left + rect.width / 2,
                    y: rect.top - containerRect.top + rect.height / 2
                });
            }
        }
    }
    
    createCompletionParticles() {
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                this.createParticle('completion');
            }, i * 25);
        }
    }
    
    createParticle(type, position = null) {
        const particle = document.createElement('div');
        particle.className = 'upload-3d-particle';
        
        const colors = {
            drag: ['#60a5fa', '#a78bfa'],
            success: ['#22c55e', '#34d399'],
            error: ['#ef4444', '#f87171'],
            remove: ['#f59e0b', '#fbbf24'],
            completion: ['#60a5fa', '#a78bfa', '#f472b6']
        };
        
        const typeColors = colors[type] || colors.drag;
        const color = typeColors[Math.floor(Math.random() * typeColors.length)];
        
        particle.style.background = color;
        particle.style.boxShadow = `0 0 10px ${color}`;
        
        if (position) {
            particle.style.left = `${position.x}px`;
            particle.style.top = `${position.y}px`;
        } else {
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
        }
        
        this.particlesContainer.appendChild(particle);
        
        // Animate particle
        const duration = 2000 + Math.random() * 1000;
        const distance = 50 + Math.random() * 100;
        const angle = Math.random() * Math.PI * 2;
        
        particle.animate([
            {
                opacity: 0,
                transform: 'translateZ(0) translateY(0) scale(0)'
            },
            {
                opacity: 1,
                transform: `translateZ(50px) translateY(-20px) scale(1)`
            },
            {
                opacity: 0,
                transform: `translateZ(100px) translateY(${-distance}px) translateX(${Math.cos(angle) * distance}px) scale(0.5)`
            }
        ], {
            duration: duration,
            easing: 'ease-out'
        }).onfinish = () => particle.remove();
    }
    
    // Public methods
    getFiles() {
        return this.files;
    }
    
    clearFiles() {
        this.files = [];
        this.updateFileList();
    }
    
    setAcceptedTypes(types) {
        this.fileInput.accept = types;
    }
    
    setMultipleAllowed(allowed) {
        this.fileInput.multiple = allowed;
    }
}

// Auto-initialize upload areas
document.addEventListener('DOMContentLoaded', () => {
    const uploadContainers = document.querySelectorAll('.upload-3d-container');
    uploadContainers.forEach(container => {
        new Upload3D(container);
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Upload3D;
}