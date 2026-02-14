// Global variables
let currentVideos = [];
let currentComments = [];
let currentChart = null;
let currentFilter = 'all';

// DOM Elements
const searchForm = document.getElementById('searchForm');
const searchBtn = document.getElementById('searchBtn');
const videosSection = document.getElementById('videosSection');
const videosList = document.getElementById('videosList');
const analysisSection = document.getElementById('analysisSection');
const quotaValue = document.getElementById('quotaValue');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateQuota();
});

function setupEventListeners() {
    searchForm.addEventListener('submit', handleSearch);
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            filterComments(currentFilter);
        });
    });
    
    // Export buttons
    document.getElementById('exportCsvBtn').addEventListener('click', () => exportData('csv'));
    document.getElementById('exportJsonBtn').addEventListener('click', () => exportData('json'));
}

async function handleSearch(e) {
    e.preventDefault();
    
    const query = document.getElementById('searchQuery').value;
    const maxResults = document.getElementById('maxResults').value;
    
    setLoading(searchBtn, true);
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, max_results: parseInt(maxResults) })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentVideos = data.videos;
        displayVideos(data.videos);
        updateQuota(data.quota);
        
    } catch (error) {
        alert('Error searching videos: ' + error.message);
    } finally {
        setLoading(searchBtn, false);
    }
}

function displayVideos(videos) {
    if (!videos || videos.length === 0) {
        videosList.innerHTML = '<p style="color: var(--text-muted);">Tidak ada video ditemukan</p>';
        videosSection.style.display = 'block';
        return;
    }
    
    videosList.innerHTML = videos.map(video => `
        <div class="video-item" data-video-id="${video.video_id}">
            <div class="video-title">${escapeHtml(video.title)}</div>
            <div class="video-meta">
                <span>📺 ${escapeHtml(video.channel)}</span>
                <span>📅 ${formatDate(video.published_at)}</span>
            </div>
            <div class="video-description">${escapeHtml(truncate(video.description, 150))}</div>
            <button class="btn btn-primary btn-sm analyze-btn" onclick="analyzeVideo('${video.video_id}', '${escapeHtml(video.title)}')">
                <span class="btn-text">Analisis Komentar</span>
                <span class="loader" style="display: none;"></span>
            </button>
        </div>
    `).join('');
    
    videosSection.style.display = 'block';
}

async function analyzeVideo(videoId, videoTitle) {
    const btn = event.target.closest('.analyze-btn');
    setLoading(btn, true);
    
    // Highlight selected video
    document.querySelectorAll('.video-item').forEach(item => item.classList.remove('selected'));
    event.target.closest('.video-item').classList.add('selected');
    
    try {
        const query = document.getElementById('searchQuery').value;
        
        const response = await fetch('/api/analyze-video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                video_id: videoId, 
                max_comments: 100,
                query: query
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentComments = data.comments;
        displayAnalysis(data.comments, data.statistics);
        updateQuota(data.quota);
        
        // Scroll to analysis
        analysisSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error analyzing video: ' + error.message);
    } finally {
        setLoading(btn, false);
    }
}

function displayAnalysis(comments, stats) {
    // Update statistics
    document.getElementById('totalComments').textContent = stats.total;
    document.getElementById('positiveCount').textContent = stats.positive;
    document.getElementById('positivePercent').textContent = stats.positive_pct + '%';
    document.getElementById('neutralCount').textContent = stats.neutral;
    document.getElementById('neutralPercent').textContent = stats.neutral_pct + '%';
    document.getElementById('negativeCount').textContent = stats.negative;
    document.getElementById('negativePercent').textContent = stats.negative_pct + '%';
    
    // Update chart
    updateChart(stats);
    
    // Display comments
    displayComments(comments);
    
    // Show analysis section
    analysisSection.style.display = 'block';
}

function updateChart(stats) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    currentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positif', 'Netral', 'Negatif'],
            datasets: [{
                data: [stats.positive, stats.neutral, stats.negative],
                backgroundColor: [
                    'hsl(142, 71%, 45%)',
                    'hsl(210, 10%, 60%)',
                    'hsl(0, 84%, 60%)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'hsl(0, 0%, 95%)',
                        font: { size: 14, family: 'Inter' },
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'hsl(220, 18%, 20%)',
                    titleColor: 'hsl(0, 0%, 95%)',
                    bodyColor: 'hsl(0, 0%, 70%)',
                    borderColor: 'hsl(220, 18%, 28%)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function displayComments(comments) {
    const commentsList = document.getElementById('commentsList');
    
    if (!comments || comments.length === 0) {
        commentsList.innerHTML = '<p style="color: var(--text-muted);">Tidak ada komentar ditemukan</p>';
        return;
    }
    
    commentsList.innerHTML = comments.map(comment => `
        <div class="comment-item ${comment.sentiment}" data-sentiment="${comment.sentiment}">
            <div class="comment-header">
                <span class="comment-author">👤 ${escapeHtml(comment.author)}</span>
                <span class="comment-sentiment sentiment-${comment.sentiment}">
                    ${getSentimentEmoji(comment.sentiment)} ${capitalize(comment.sentiment)}
                </span>
            </div>
            <div class="comment-text">${escapeHtml(comment.text)}</div>
            <div class="comment-meta">
                <span>👍 ${comment.likes}</span>
                <span>📅 ${formatDate(comment.published_at)}</span>
                <span>📊 Score: ${comment.sentiment_score.toFixed(3)}</span>
            </div>
        </div>
    `).join('');
}

function filterComments(filter) {
    const commentItems = document.querySelectorAll('.comment-item');
    
    commentItems.forEach(item => {
        if (filter === 'all' || item.dataset.sentiment === filter) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

async function exportData(format) {
    if (!currentComments || currentComments.length === 0) {
        alert('Tidak ada data untuk di-export');
        return;
    }
    
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                comments: currentComments,
                format: format
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Data berhasil di-export ke: ${data.filepath}`);
        } else {
            alert('Error exporting data');
        }
        
    } catch (error) {
        alert('Error exporting data: ' + error.message);
    }
}

async function updateQuota(quotaData = null) {
    if (quotaData) {
        quotaValue.textContent = `${quotaData.quota_used} / ${quotaData.daily_limit}`;
        return;
    }
    
    try {
        const response = await fetch('/api/quota');
        const data = await response.json();
        quotaValue.textContent = `${data.quota_used} / ${data.daily_limit}`;
    } catch (error) {
        quotaValue.textContent = 'Error';
    }
}

// Utility functions
function setLoading(btn, loading) {
    const btnText = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    
    if (loading) {
        btn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'block';
    } else {
        btn.disabled = false;
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function getSentimentEmoji(sentiment) {
    const emojis = {
        'positive': '😊',
        'neutral': '😐',
        'negative': '😞'
    };
    return emojis[sentiment] || '😐';
}

function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}
