// Exercise Tutorial Animations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations when the page loads
    initializeAnimations();
    
    // Set up filter buttons for exercise categories
    setupCategoryFilters();
    
    // Set up play/pause buttons for animations in modals
    setupPlayPauseButtons();
});

// Initialize Lottie animations
function initializeAnimations() {
    // Push-up animations
    const pushUpAnim = lottie.loadAnimation({
        container: document.getElementById('push-up-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/push-up.json'
    });
    
    const pushUpAnimModal = lottie.loadAnimation({
        container: document.getElementById('push-up-animation-modal'),
        renderer: 'svg',
        loop: false,
        autoplay: false,
        path: '/static/animations/push-up.json'
    });
    
    // Squat animations
    const squatAnim = lottie.loadAnimation({
        container: document.getElementById('squat-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/squat.json'
    });
    
    const squatAnimModal = lottie.loadAnimation({
        container: document.getElementById('squat-animation-modal'),
        renderer: 'svg',
        loop: false,
        autoplay: false,
        path: '/static/animations/squat.json'
    });
    
    // Jumping Jack animations
    const jumpingJackAnim = lottie.loadAnimation({
        container: document.getElementById('jumping-jack-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/jumping-jack.json'
    });

    const jumpingJackAnimModal = lottie.loadAnimation({
        container: document.getElementById('jumping-jack-animation-modal'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/jumping-jack.json'
    });
    
    // Hamstring Stretch animations
    const hamstringStretchAnim = lottie.loadAnimation({
        container: document.getElementById('hamstring-stretch-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/hamstring-stretch.json'
    });
    
    // Tree Pose animations
    const treePoseAnim = lottie.loadAnimation({
        container: document.getElementById('tree-pose-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/tree-pose.json'
    });
    
    // Plank animations
    const plankAnim = lottie.loadAnimation({
        container: document.getElementById('plank-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/animations/plank.json'
    });
    
    // Store animations in global object for later access
    window.exerciseAnimations = {
        pushUpAnim: pushUpAnim,
        pushUpAnimModal: pushUpAnimModal,
        squatAnim: squatAnim,
        squatAnimModal: squatAnimModal,
        jumpingJackAnim: jumpingJackAnim,
        jumpingJackAnimModal: jumpingJackAnimModal,
        hamstringStretchAnim: hamstringStretchAnim,
        treePoseAnim: treePoseAnim,
        plankAnim: plankAnim
    };
}

// Set up filtering by exercise category
function setupCategoryFilters() {
    const filterButtons = document.querySelectorAll('.exercise-filter');
    const exerciseItems = document.querySelectorAll('.exercise-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const category = this.getAttribute('data-category');
            
            // Show/hide exercises based on category
            exerciseItems.forEach(item => {
                if (category === 'all' || item.getAttribute('data-category') === category) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

// Set up play/pause buttons for animations in modals
function setupPlayPauseButtons() {
    // Push-up play button
    const pushUpPlayBtn = document.getElementById('push-up-play');
    if (pushUpPlayBtn) {
        pushUpPlayBtn.addEventListener('click', function() {
            const anim = window.exerciseAnimations.pushUpAnimModal;
            if (anim) {
                if (this.textContent === 'Play Animation') {
                    anim.goToAndPlay(0);
                    this.textContent = 'Pause Animation';
                } else {
                    anim.pause();
                    this.textContent = 'Play Animation';
                }
            }
        });
    }
    
    // Squat play button
    const squatPlayBtn = document.getElementById('squat-play');
    if (squatPlayBtn) {
        squatPlayBtn.addEventListener('click', function() {
            const anim = window.exerciseAnimations.squatAnimModal;
            if (anim) {
                if (this.textContent === 'Play Animation') {
                    anim.goToAndPlay(0);
                    this.textContent = 'Pause Animation';
                } else {
                    anim.pause();
                    this.textContent = 'Play Animation';
                }
            }
        });
    }

    const jumpingJackPlayBtn = document.getElementById('jumping-jack-play');
    if (jumpingJackPlayBtn) {
        jumpingJackPlayBtn.addEventListener('click', function() {
            const anim = window.exerciseAnimations.jumpingJackAnimModal;
            if (anim) {
                if (this.textContent === 'Play Animation') {
                    anim.goToAndPlay(0);
                    this.textContent = 'Pause Animation';
                } else {
                    anim.pause();
                    this.textContent = 'Play Animation';
                }
            }
        });
    }
    
    // Reset animation play button text when modals are closed
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const playBtn = this.querySelector('.btn-primary');
            if (playBtn) {
                playBtn.textContent = 'Play Animation';
            }
        });
    });
}

// Fallback functions for handling errors in animation loading
function handleAnimationError(animElement, exerciseName) {
    if (animElement) {
        animElement.innerHTML = `
            <div class="animation-fallback">
                <i class="fas fa-exclamation-circle fa-3x mb-3"></i>
                <p>Animation for ${exerciseName} could not be loaded.</p>
            </div>
        `;
    }
}