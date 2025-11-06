// Teaching Resources Hub - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Teaching Resources Hub loaded successfully!');

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation to feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s, transform 0.5s';
        observer.observe(card);
    });

    // Log helpful message for developers
    console.log('💡 Ready to add more features! Check out app/routes.py to add new tools.');

    // Homepage search functionality
    initHomepageSearch();

    // Resources page functionality
    initResourcesPage();
});

// Homepage Search Functionality with Autocomplete
function initHomepageSearch() {
    const heroSearchInput = document.getElementById('heroSearch');
    const heroSearchBtn = document.getElementById('heroSearchBtn');
    const autocompleteDropdown = document.getElementById('autocompleteDropdown');
    const autocompleteResults = document.getElementById('autocompleteResults');
    const autocompleteFooter = document.getElementById('autocompleteFooter');
    const autocompleteCount = document.getElementById('autocompleteCount');

    if (!heroSearchInput || !heroSearchBtn) return;

    let allResources = [];
    let selectedIndex = -1;

    // Fetch resources data on page load
    fetch('/api/resources')
        .then(response => response.json())
        .then(data => {
            allResources = data.resources || [];
            console.log(`Loaded ${allResources.length} resources for autocomplete`);
        })
        .catch(error => console.error('Error loading resources:', error));

    // Function to navigate to resources with search
    function navigateToResources(searchTerm = null) {
        const term = searchTerm || heroSearchInput.value.trim();
        if (term) {
            window.location.href = `/resources?search=${encodeURIComponent(term)}`;
        } else {
            window.location.href = '/resources';
        }
    }

    // Function to show autocomplete results
    function showAutocomplete(searchTerm) {
        if (!searchTerm || searchTerm.length < 2) {
            hideAutocomplete();
            return;
        }

        const lowerSearch = searchTerm.toLowerCase();
        const matches = allResources.filter(resource => {
            return resource.name.toLowerCase().includes(lowerSearch) ||
                   resource.description.toLowerCase().includes(lowerSearch) ||
                   resource.category.toLowerCase().includes(lowerSearch) ||
                   resource.tags.some(tag => tag.toLowerCase().includes(lowerSearch));
        });

        if (matches.length === 0) {
            hideAutocomplete();
            return;
        }

        // Show top 8 matches
        const topMatches = matches.slice(0, 8);
        autocompleteResults.innerHTML = '';

        topMatches.forEach((resource, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.setAttribute('data-index', index);

            // Highlight matching text
            const nameParts = highlightMatch(resource.name, searchTerm);

            item.innerHTML = `
                <div class="autocomplete-item-icon">${resource.category_icon}</div>
                <div class="autocomplete-item-content">
                    <div class="autocomplete-item-name">${nameParts}</div>
                    <div class="autocomplete-item-category">${resource.category}</div>
                </div>
                <div class="autocomplete-item-tags">
                    ${resource.tags.slice(0, 2).map(tag =>
                        `<span class="autocomplete-tag">${tag}</span>`
                    ).join('')}
                </div>
            `;

            item.addEventListener('click', () => {
                navigateToResources(resource.name);
            });

            item.addEventListener('mouseenter', () => {
                selectedIndex = index;
                updateSelectedItem();
            });

            autocompleteResults.appendChild(item);
        });

        // Show "See all X results" footer
        if (matches.length > 8) {
            autocompleteCount.textContent = `See all ${matches.length} results →`;
            autocompleteFooter.style.display = 'block';
            autocompleteFooter.onclick = () => navigateToResources(searchTerm);
        } else if (matches.length > 1) {
            autocompleteCount.textContent = `${matches.length} resources found →`;
            autocompleteFooter.style.display = 'block';
            autocompleteFooter.onclick = () => navigateToResources(searchTerm);
        } else {
            autocompleteFooter.style.display = 'none';
        }

        autocompleteDropdown.style.display = 'block';
        selectedIndex = -1;
    }

    function hideAutocomplete() {
        autocompleteDropdown.style.display = 'none';
        selectedIndex = -1;
    }

    function highlightMatch(text, search) {
        const regex = new RegExp(`(${search})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    function updateSelectedItem() {
        const items = autocompleteResults.querySelectorAll('.autocomplete-item');
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    // Input event for live search
    heroSearchInput.addEventListener('input', function() {
        showAutocomplete(this.value);
    });

    // Keyboard navigation
    heroSearchInput.addEventListener('keydown', function(e) {
        const items = autocompleteResults.querySelectorAll('.autocomplete-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelectedItem();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelectedItem();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex >= 0 && items[selectedIndex]) {
                items[selectedIndex].click();
            } else {
                navigateToResources();
            }
        } else if (e.key === 'Escape') {
            hideAutocomplete();
        }
    });

    // Button click
    heroSearchBtn.addEventListener('click', () => navigateToResources());

    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!heroSearchInput.contains(e.target) && !autocompleteDropdown.contains(e.target)) {
            hideAutocomplete();
        }
    });

    console.log('Homepage search with autocomplete initialized!');
}

// Resources Page Search and Filter Functionality - Enhanced
function initResourcesPage() {
    // Only run on resources page
    const searchInput = document.getElementById('resourceSearch');
    if (!searchInput) return;

    const clearButton = document.getElementById('clearSearch');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const tagFilters = document.querySelectorAll('.tag-filter');
    const resourceCards = document.querySelectorAll('.resource-card, .resource-card-enhanced');
    const categorySection = document.querySelectorAll('.category-section, .category-section-enhanced');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const visibleCountSpan = document.getElementById('visibleCount');
    const categoryCountSpan = document.getElementById('categoryCount');
    const categoryJump = document.getElementById('categoryJump');
    const scrollToTopBtn = document.getElementById('scrollToTop');
    const resetFiltersBtn = document.getElementById('resetFilters');

    let activeTag = 'all';

    // Search functionality
    searchInput.addEventListener('input', function() {
        filterResources();
    });

    // Clear search
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            filterResources();
        });
    }

    // Enhanced filter button functionality
    if (filterButtons.length > 0) {
        filterButtons.forEach(filter => {
            filter.addEventListener('click', function() {
                // Remove active class from all filters
                filterButtons.forEach(f => f.classList.remove('active'));

                // Add active class to clicked filter
                this.classList.add('active');

                // Set active tag
                activeTag = this.getAttribute('data-tag');

                // Filter resources
                filterResources();
            });
        });
    }

    // Legacy tag filter functionality (for old template)
    tagFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            tagFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            activeTag = this.getAttribute('data-tag');
            filterResources();
        });
    });

    // Category toggle functionality - Enhanced
    const toggleButtons = document.querySelectorAll('.toggle-category, .toggle-category-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const categorySection = this.closest('.category-section, .category-section-enhanced');
            const resourcesGrid = categorySection.querySelector('.resources-grid, .resources-grid-enhanced');
            const isExpanded = this.getAttribute('data-expanded') === 'true';

            if (isExpanded) {
                resourcesGrid.classList.add('collapsed');
                this.setAttribute('data-expanded', 'false');
                // Update button text if it's not using SVG
                if (!this.querySelector('svg')) {
                    this.textContent = 'Expand';
                }
            } else {
                resourcesGrid.classList.remove('collapsed');
                this.setAttribute('data-expanded', 'true');
                if (!this.querySelector('svg')) {
                    this.textContent = 'Collapse';
                }
            }
        });
    });

    // Category Jump functionality
    if (categoryJump) {
        categoryJump.addEventListener('change', function() {
            const categoryName = this.value;
            if (categoryName) {
                const categoryElement = document.getElementById(categoryName);
                if (categoryElement) {
                    categoryElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    // Reset select
                    setTimeout(() => {
                        this.value = '';
                    }, 500);
                }
            }
        });
    }

    // Scroll to Top functionality
    if (scrollToTopBtn) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.style.display = 'flex';
            } else {
                scrollToTopBtn.style.display = 'none';
            }
        });

        // Scroll to top on click
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Reset Filters functionality
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            searchInput.value = '';
            activeTag = 'all';

            // Reset filter buttons
            filterButtons.forEach(f => f.classList.remove('active'));
            const allButton = document.querySelector('[data-tag="all"]');
            if (allButton) {
                allButton.classList.add('active');
            }

            filterResources();
        });
    }

    // Main filter function
    function filterResources() {
        const searchTerm = searchInput.value.toLowerCase();
        let visibleResources = 0;
        let visibleCategories = 0;

        categorySection.forEach(category => {
            const cards = category.querySelectorAll('.resource-card, .resource-card-enhanced');
            let categoryHasVisibleCards = false;

            cards.forEach(card => {
                const name = card.getAttribute('data-name');
                const description = card.getAttribute('data-description');
                const tags = card.getAttribute('data-tags');

                // Check search match
                const matchesSearch = searchTerm === '' ||
                                     name.includes(searchTerm) ||
                                     description.includes(searchTerm) ||
                                     tags.includes(searchTerm);

                // Check tag filter match
                const matchesTag = activeTag === 'all' || tags.includes(activeTag);

                // Show or hide card
                if (matchesSearch && matchesTag) {
                    card.classList.remove('hidden');
                    card.style.display = '';
                    categoryHasVisibleCards = true;
                    visibleResources++;
                } else {
                    card.classList.add('hidden');
                    card.style.display = 'none';
                }
            });

            // Show or hide category section
            if (categoryHasVisibleCards) {
                category.classList.remove('hidden');
                category.style.display = '';
                visibleCategories++;
            } else {
                category.classList.add('hidden');
                category.style.display = 'none';
            }
        });

        // Update stats
        if (visibleCountSpan) {
            visibleCountSpan.textContent = visibleResources;
        }
        if (categoryCountSpan) {
            categoryCountSpan.textContent = visibleCategories;
        }

        // Show/hide no results message
        if (noResultsMessage) {
            if (visibleResources === 0) {
                noResultsMessage.style.display = 'block';
            } else {
                noResultsMessage.style.display = 'none';
            }
        }
    }

    // Check for URL search parameter and auto-populate
    const urlParams = new URLSearchParams(window.location.search);
    const searchParam = urlParams.get('search');
    if (searchParam) {
        searchInput.value = searchParam;
        // Trigger search automatically
        filterResources();
        // Scroll to top to show search results
        window.scrollTo({ top: 0, behavior: 'smooth' });
        console.log(`Auto-searched for: "${searchParam}"`);
    }

    console.log('Enhanced resources page functionality initialized!');

    // Initialize advanced filters
    initAdvancedFilters();
}


// Advanced Filters Enhancement for Resources Page
function initAdvancedFilters() {
    const toggleFiltersBtn = document.getElementById('toggleFilters');
    const advancedFiltersPanel = document.getElementById('advancedFilters');
    const closeFiltersBtn = document.getElementById('closeFilters');
    const clearAllFiltersBtn = document.getElementById('clearAllFilters');
    const clearActiveFiltersBtn = document.getElementById('clearActiveFilters');
    const sortSelect = document.getElementById('sortResources');
    const activeFiltersContainer = document.getElementById('activeFiltersContainer');
    const activeFiltersPills = document.getElementById('activeFiltersPills');

    if (!toggleFiltersBtn) return; // Not on resources page

    let activeFilters = {
        cost: [],
        grade: [],
        subject: []
    };

    // Toggle filters panel
    if (toggleFiltersBtn) {
        toggleFiltersBtn.addEventListener('click', function() {
            const isVisible = advancedFiltersPanel.style.display !== 'none';
            advancedFiltersPanel.style.display = isVisible ? 'none' : 'block';
        });
    }

    // Close filters panel
    if (closeFiltersBtn) {
        closeFiltersBtn.addEventListener('click', function() {
            advancedFiltersPanel.style.display = 'none';
        });
    }

    // Get all filter checkboxes
    const costCheckboxes = document.querySelectorAll('input[name="cost"]');
    const gradeCheckboxes = document.querySelectorAll('input[name="grade"]');
    const subjectCheckboxes = document.querySelectorAll('input[name="subject"]');

    // Function to update active filters
    function updateActiveFilters() {
        activeFilters.cost = Array.from(costCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
        activeFilters.grade = Array.from(gradeCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
        activeFilters.subject = Array.from(subjectCheckboxes).filter(cb => cb.checked).map(cb => cb.value);

        updateActiveFiltersPills();
        applyAllFilters();
    }

    // Add event listeners to all checkboxes
    [...costCheckboxes, ...gradeCheckboxes, ...subjectCheckboxes].forEach(checkbox => {
        checkbox.addEventListener('change', updateActiveFilters);
    });

    // Update active filters pills display
    function updateActiveFiltersPills() {
        activeFiltersPills.innerHTML = '';
        let hasFilters = false;

        // Check if not all filters are selected (meaning user has deselected some)
        const allSelected = areAllFiltersSelected();

        if (!allSelected) {
            // Add cost pills for selected filters
            activeFilters.cost.forEach(filter => {
                addFilterPill('Cost', filter, 'cost');
                hasFilters = true;
            });

            // Add grade pills
            activeFilters.grade.forEach(filter => {
                addFilterPill('Grade', filter, 'grade');
                hasFilters = true;
            });

            // Add subject pills
            activeFilters.subject.forEach(filter => {
                addFilterPill('Subject', filter, 'subject');
                hasFilters = true;
            });
        }

        // Show/hide active filters container
        activeFiltersContainer.style.display = hasFilters ? 'block' : 'none';
    }

    function areAllFiltersSelected() {
        return activeFilters.cost.length === costCheckboxes.length &&
               activeFilters.grade.length === gradeCheckboxes.length &&
               activeFilters.subject.length === subjectCheckboxes.length;
    }

    function addFilterPill(type, value, filterType) {
        const pill = document.createElement('div');
        pill.className = 'filter-pill';
        pill.innerHTML = `
            <span class="pill-label">${type}:</span>
            <span class="pill-value">${formatFilterValue(value)}</span>
            <button class="pill-remove" data-type="${filterType}" data-value="${value}">×</button>
        `;

        pill.querySelector('.pill-remove').addEventListener('click', function() {
            removeFilter(filterType, value);
        });

        activeFiltersPills.appendChild(pill);
    }

    function formatFilterValue(value) {
        const labels = {
            'free': 'Free',
            'freemium': 'Freemium',
            'paid': 'Premium/Paid',
            'pre-k': 'Pre-K',
            'elementary': 'Elementary',
            'middle': 'Middle School',
            'high': 'High School',
            'college': 'College',
            'k-12': 'K-12',
            'math': 'Mathematics',
            'science': 'Science',
            'ela': 'ELA/Literacy',
            'social': 'Social Studies',
            'arts': 'Arts & Music',
            'pe': 'PE/Health',
            'languages': 'Languages',
            'cs': 'CS/Tech'
        };
        return labels[value] || value;
    }

    function removeFilter(type, value) {
        const checkbox = document.querySelector(`input[name="${type}"][value="${value}"]`);
        if (checkbox) {
            checkbox.checked = false;
            updateActiveFilters();
        }
    }

    // Clear all filters
    if (clearAllFiltersBtn) {
        clearAllFiltersBtn.addEventListener('click', function() {
            [...costCheckboxes, ...gradeCheckboxes, ...subjectCheckboxes].forEach(cb => {
                cb.checked = true; // Set all to checked (show all)
            });
            updateActiveFilters();
        });
    }

    if (clearActiveFiltersBtn) {
        clearActiveFiltersBtn.addEventListener('click', function() {
            [...costCheckboxes, ...gradeCheckboxes, ...subjectCheckboxes].forEach(cb => {
                cb.checked = true;
            });
            updateActiveFilters();
        });
    }

    // Sort functionality
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            sortResources(this.value);
        });
    }

    function sortResources(sortType) {
        const container = document.querySelector('.resources-container-enhanced');
        if (!container) return;

        const sections = Array.from(container.querySelectorAll('.category-section-enhanced'));

        if (sortType === 'az' || sortType === 'za') {
            // Sort categories alphabetically
            sections.sort((a, b) => {
                const nameA = a.getAttribute('data-category').toLowerCase();
                const nameB = b.getAttribute('data-category').toLowerCase();
                return sortType === 'az' ? nameA.localeCompare(nameB) : nameB.localeCompare(nameA);
            });

            sections.forEach(section => container.appendChild(section));
        }
    }

    // Apply all filters
    function applyAllFilters() {
        const searchInput = document.getElementById('resourceSearch');
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';

        const categorySection = document.querySelectorAll('.category-section, .category-section-enhanced');
        const visibleCountSpan = document.getElementById('visibleCount');
        const categoryCountSpan = document.getElementById('categoryCount');
        const noResultsMessage = document.getElementById('noResultsMessage');

        let visibleResources = 0;
        let visibleCategories = 0;

        const allSelected = areAllFiltersSelected();

        categorySection.forEach(category => {
            const cards = category.querySelectorAll('.resource-card, .resource-card-enhanced');
            let categoryHasVisibleCards = false;

            cards.forEach(card => {
                const name = card.getAttribute('data-name') || '';
                const description = card.getAttribute('data-description') || '';
                const tags = (card.getAttribute('data-tags') || '').toLowerCase();

                // Check search match
                const matchesSearch = searchTerm === '' ||
                                     name.includes(searchTerm) ||
                                     description.includes(searchTerm) ||
                                     tags.includes(searchTerm);

                let matchesCost = allSelected;
                let matchesGrade = allSelected;
                let matchesSubject = allSelected;

                if (!allSelected) {
                    // Check cost filters
                    matchesCost = activeFilters.cost.length === 0 ||
                                       activeFilters.cost.some(cost => {
                                           if (cost === 'free') return tags.includes('free') && !tags.includes('freemium');
                                           if (cost === 'freemium') return tags.includes('freemium');
                                           if (cost === 'paid') return tags.includes('paid') || tags.includes('premium');
                                           return false;
                                       });

                    // Check grade level filters
                    matchesGrade = activeFilters.grade.length === 0 ||
                                        activeFilters.grade.some(grade => {
                                            if (grade === 'pre-k') return tags.includes('pre-k') || tags.includes('prek');
                                            if (grade === 'elementary') return tags.includes('elementary') || tags.includes('k-5');
                                            if (grade === 'middle') return tags.includes('middle') || tags.includes('6-8');
                                            if (grade === 'high') return tags.includes('high school') || tags.includes('9-12');
                                            if (grade === 'college') return tags.includes('college') || tags.includes('higher ed');
                                            if (grade === 'k-12') return tags.includes('k-12');
                                            return false;
                                        });

                    // Check subject filters
                    matchesSubject = activeFilters.subject.length === 0 ||
                                          activeFilters.subject.some(subject => {
                                              if (subject === 'math') return tags.includes('math');
                                              if (subject === 'science') return tags.includes('science');
                                              if (subject === 'ela') return tags.includes('reading') || tags.includes('writing') || tags.includes('literacy') || tags.includes('ela');
                                              if (subject === 'social') return tags.includes('social studies') || tags.includes('history') || tags.includes('geography');
                                              if (subject === 'arts') return tags.includes('art') || tags.includes('music');
                                              if (subject === 'pe') return tags.includes('pe') || tags.includes('health') || tags.includes('physical');
                                              if (subject === 'languages') return tags.includes('language') || tags.includes('spanish') || tags.includes('french');
                                              if (subject === 'cs') return tags.includes('coding') || tags.includes('computer') || tags.includes('tech');
                                              return false;
                                          });
                }

                // Show or hide card based on all criteria
                const matches = matchesSearch && matchesCost && matchesGrade && matchesSubject;

                if (matches) {
                    card.classList.remove('hidden');
                    card.style.display = '';
                    categoryHasVisibleCards = true;
                    visibleResources++;
                } else {
                    card.classList.add('hidden');
                    card.style.display = 'none';
                }
            });

            // Show or hide category section
            if (categoryHasVisibleCards) {
                category.classList.remove('hidden');
                category.style.display = '';
                visibleCategories++;
            } else {
                category.classList.add('hidden');
                category.style.display = 'none';
            }
        });

        // Update stats
        if (visibleCountSpan) {
            visibleCountSpan.textContent = visibleResources;
        }
        if (categoryCountSpan) {
            categoryCountSpan.textContent = visibleCategories;
        }

        // Show/hide no results message
        if (noResultsMessage) {
            if (visibleResources === 0) {
                noResultsMessage.style.display = 'block';
            } else {
                noResultsMessage.style.display = 'none';
            }
        }
    }

    // Initialize with all filters selected
    updateActiveFilters();

    // Also connect to search input
    const searchInput = document.getElementById('resourceSearch');
    if (searchInput) {
        searchInput.removeEventListener('input', function() {}); // Remove old listener
        searchInput.addEventListener('input', applyAllFilters);
    }

    console.log('Advanced filters initialized!');
}

// ========================================
// SETTINGS PANEL FUNCTIONALITY
// ========================================

function initSettingsPanel() {
    const settingsToggle = document.getElementById('settingsToggle');
    const settingsPanel = document.getElementById('settingsPanel');
    const settingsOverlay = document.getElementById('settingsOverlay');
    const closeSettings = document.getElementById('closeSettings');
    const saveSettings = document.getElementById('saveSettings');
    const resetSettings = document.getElementById('resetSettings');

    if (!settingsToggle) return; // Only on resources page

    // Default settings (all on for full information display)
    const defaultSettings = {
        statsBar: true,
        categoryJump: true,
        filterSort: true,
        resourcesFooter: true,
        categoryDescriptions: true,
        categoryBadges: true,
        resourceDescriptions: true,
        resourceTags: true,
        cardSpacing: 'normal'
    };

    // Load settings from localStorage or use defaults
    let currentSettings = loadSettings();

    // Apply settings on page load
    applySettings(currentSettings, false);

    // Open settings panel
    function openSettingsPanel() {
        settingsPanel.style.display = 'flex';
        settingsOverlay.style.display = 'block';
        document.body.style.overflow = 'hidden';

        // Update checkboxes to match current settings
        document.getElementById('toggleStatsBar').checked = currentSettings.statsBar;
        document.getElementById('toggleCategoryJump').checked = currentSettings.categoryJump;
        document.getElementById('toggleFilterSort').checked = currentSettings.filterSort;
        document.getElementById('toggleResourcesFooter').checked = currentSettings.resourcesFooter;
        document.getElementById('toggleCategoryDescriptions').checked = currentSettings.categoryDescriptions;
        document.getElementById('toggleCategoryBadges').checked = currentSettings.categoryBadges;
        document.getElementById('toggleResourceDescriptions').checked = currentSettings.resourceDescriptions;
        document.getElementById('toggleResourceTags').checked = currentSettings.resourceTags;

        // Update radio buttons
        const spacingRadios = document.querySelectorAll('input[name="cardSpacing"]');
        spacingRadios.forEach(radio => {
            radio.checked = radio.value === currentSettings.cardSpacing;
        });
    }

    // Close settings panel
    function closeSettingsPanel() {
        settingsPanel.style.display = 'none';
        settingsOverlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    // Load settings from localStorage
    function loadSettings() {
        try {
            const saved = localStorage.getItem('resourcesDisplaySettings');
            if (saved) {
                return { ...defaultSettings, ...JSON.parse(saved) };
            }
        } catch (e) {
            console.error('Error loading settings:', e);
        }
        return { ...defaultSettings };
    }

    // Save settings to localStorage
    function saveSettingsToStorage(settings) {
        try {
            localStorage.setItem('resourcesDisplaySettings', JSON.stringify(settings));
            console.log('Settings saved:', settings);
        } catch (e) {
            console.error('Error saving settings:', e);
        }
    }

    // Apply settings to the page
    function applySettings(settings, animate = true) {
        const body = document.body;

        // Apply or remove hide classes
        toggleClass(body, 'hide-stats-bar', !settings.statsBar);
        toggleClass(body, 'hide-category-jump', !settings.categoryJump);
        toggleClass(body, 'hide-filter-sort', !settings.filterSort);
        toggleClass(body, 'hide-resources-footer', !settings.resourcesFooter);
        toggleClass(body, 'hide-category-descriptions', !settings.categoryDescriptions);
        toggleClass(body, 'hide-category-badges', !settings.categoryBadges);
        toggleClass(body, 'hide-resource-descriptions', !settings.resourceDescriptions);
        toggleClass(body, 'hide-resource-tags', !settings.resourceTags);

        // Apply spacing classes
        body.classList.remove('spacing-compact', 'spacing-normal', 'spacing-spacious');
        body.classList.add(`spacing-${settings.cardSpacing}`);

        // Show feedback if animating
        if (animate) {
            showSettingsFeedback('Settings applied successfully!');
        }
    }

    // Toggle class helper
    function toggleClass(element, className, shouldAdd) {
        if (shouldAdd) {
            element.classList.add(className);
        } else {
            element.classList.remove(className);
        }
    }

    // Show feedback message
    function showSettingsFeedback(message) {
        // Create feedback element if it doesn't exist
        let feedback = document.getElementById('settingsFeedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.id = 'settingsFeedback';
            feedback.style.cssText = `
                position: fixed;
                bottom: 2rem;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 2rem;
                border-radius: 50px;
                font-weight: 600;
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
                z-index: 10000;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(feedback);
        }

        feedback.textContent = message;
        feedback.style.opacity = '1';

        setTimeout(() => {
            feedback.style.opacity = '0';
        }, 2000);
    }

    // Event listeners
    settingsToggle.addEventListener('click', openSettingsPanel);
    closeSettings.addEventListener('click', closeSettingsPanel);
    settingsOverlay.addEventListener('click', closeSettingsPanel);

    // Save settings
    saveSettings.addEventListener('click', function() {
        // Collect current settings from checkboxes
        currentSettings = {
            statsBar: document.getElementById('toggleStatsBar').checked,
            categoryJump: document.getElementById('toggleCategoryJump').checked,
            filterSort: document.getElementById('toggleFilterSort').checked,
            resourcesFooter: document.getElementById('toggleResourcesFooter').checked,
            categoryDescriptions: document.getElementById('toggleCategoryDescriptions').checked,
            categoryBadges: document.getElementById('toggleCategoryBadges').checked,
            resourceDescriptions: document.getElementById('toggleResourceDescriptions').checked,
            resourceTags: document.getElementById('toggleResourceTags').checked,
            cardSpacing: document.querySelector('input[name="cardSpacing"]:checked').value
        };

        // Apply and save
        applySettings(currentSettings, true);
        saveSettingsToStorage(currentSettings);
        closeSettingsPanel();
    });

    // Reset settings
    resetSettings.addEventListener('click', function() {
        if (confirm('Reset all display settings to default?')) {
            currentSettings = { ...defaultSettings };
            applySettings(currentSettings, true);
            saveSettingsToStorage(currentSettings);

            // Update UI
            document.getElementById('toggleStatsBar').checked = defaultSettings.statsBar;
            document.getElementById('toggleCategoryJump').checked = defaultSettings.categoryJump;
            document.getElementById('toggleFilterSort').checked = defaultSettings.filterSort;
            document.getElementById('toggleResourcesFooter').checked = defaultSettings.resourcesFooter;
            document.getElementById('toggleCategoryDescriptions').checked = defaultSettings.categoryDescriptions;
            document.getElementById('toggleCategoryBadges').checked = defaultSettings.categoryBadges;
            document.getElementById('toggleResourceDescriptions').checked = defaultSettings.resourceDescriptions;
            document.getElementById('toggleResourceTags').checked = defaultSettings.resourceTags;

            const spacingRadios = document.querySelectorAll('input[name="cardSpacing"]');
            spacingRadios.forEach(radio => {
                radio.checked = radio.value === defaultSettings.cardSpacing;
            });

            showSettingsFeedback('Settings reset to default!');
        }
    });

    // Close panel with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && settingsPanel.style.display === 'flex') {
            closeSettingsPanel();
        }
    });

    console.log('Settings panel initialized with settings:', currentSettings);
}

// Initialize settings panel on page load
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure resources page is loaded
    setTimeout(initSettingsPanel, 100);

    // Initialize favorites functionality
    initFavorites();
});

// ===============================================
// FAVORITES FUNCTIONALITY
// ===============================================

let userFavorites = new Set();

function initFavorites() {
    // Only run on resources page and if user is authenticated
    if (!document.querySelector('.resources-grid-enhanced')) {
        return;
    }

    // Check if user is authenticated by looking for favorite buttons
    const favButtons = document.querySelectorAll('.favorite-btn');
    if (favButtons.length === 0) {
        return;
    }

    // Load user's favorites
    loadUserFavorites();
}

function loadUserFavorites() {
    // Get all resource IDs on the page
    const resourceIds = Array.from(document.querySelectorAll('.resource-card-enhanced')).map(card =>
        card.getAttribute('data-resource-id')
    );

    if (resourceIds.length === 0) {
        return;
    }

    // Check which resources are favorited
    fetch('/api/favorites/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resource_ids: resourceIds })
    })
    .then(response => response.json())
    .then(data => {
        userFavorites = new Set(Object.keys(data.favorited || {}));
        updateFavoriteButtons();
    })
    .catch(error => {
        console.error('Error loading favorites:', error);
    });
}

function updateFavoriteButtons() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        const resourceId = btn.getAttribute('data-resource-id');
        if (userFavorites.has(resourceId)) {
            btn.classList.add('favorited');
            btn.textContent = '⭐';
            btn.title = 'Remove from favorites';
        } else {
            btn.classList.remove('favorited');
            btn.textContent = '☆';
            btn.title = 'Add to favorites';
        }
    });
}

function toggleFavorite(event, resourceId, resourceName) {
    event.preventDefault();
    event.stopPropagation();

    const btn = event.target;
    const isFavorited = userFavorites.has(resourceId);

    // Optimistically update UI
    btn.disabled = true;

    if (isFavorited) {
        // Remove from favorites
        fetch('/api/favorite/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_id: resourceId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                userFavorites.delete(resourceId);
                updateFavoriteButtons();
                showFavoriteNotification(`Removed "${resourceName}" from favorites`);
            } else {
                showFavoriteNotification(`Failed to remove favorite: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFavoriteNotification('Failed to remove favorite', 'error');
        })
        .finally(() => {
            btn.disabled = false;
        });
    } else {
        // Add to favorites
        fetch('/api/favorite/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_id: resourceId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                userFavorites.add(resourceId);
                updateFavoriteButtons();
                showFavoriteNotification(`Added "${resourceName}" to favorites!`);
            } else {
                showFavoriteNotification(`Failed to add favorite: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFavoriteNotification('Failed to add favorite', 'error');
        })
        .finally(() => {
            btn.disabled = false;
        });
    }
}

function showFavoriteNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `favorite-notification favorite-notification-${type}`;
    notification.textContent = message;

    // Add to page
    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}
