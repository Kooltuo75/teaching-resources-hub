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
