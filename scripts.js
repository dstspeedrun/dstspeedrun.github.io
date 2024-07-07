document.addEventListener('DOMContentLoaded', () => {
    const primitivesUrl = 'data/primitives.json';
    const craftablesUrl = 'data/ingredients.json';
    let primitives = [];
    let craftables = [];
    
    fetch(primitivesUrl)
        .then(response => response.json())
        .then(data => primitives = data);

    fetch(craftablesUrl)
        .then(response => response.json())
        .then(data => craftables = data);

    const searchInput = document.getElementById('search-input');
    const dropdown = document.getElementById('dropdown');
    const panelsContainer = document.getElementById('panels-container');
    const newPanelBtn = document.getElementById('new-panel-btn');
    const panelNameInput = document.getElementById('panel-name-input');
    const searchModal = document.getElementById('search');
    searchModal.style.display = 'none';

    let activePanel = null;
    let panelCounter = 0;

    // Load saved panels from localStorage
    loadPanelsFromStorage();

    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && !searchInput.contains(e.target) && !e.target.closest('.add-item-btn')) {
            dropdown.innerHTML = '';
            searchInput.value = '';
            closeModal();
        }
    });

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();
        dropdown.innerHTML = '';

        if (query) {
            const matches = [...primitives, ...craftables].filter(item => item.title.toLowerCase().includes(query));
            matches.forEach(item => {
                const div = document.createElement('div');
                div.className = 'dropdown-item';
                div.innerHTML = `
                    <div>
                    <img src="${item.image_url}" alt="${item.title}">${item.title}
                    </div>
                    <div>
                    ${item.crafting ? '<button class="add-multiple" data-count="0.5">x0.5</button>' : ''}
                    <button class="add-multiple" data-count="2">x2</button>
                    <button class="add-multiple" data-count="3">x3</button>
                    <button class="add-multiple" data-count="4">x4</button>
                    <button class="add-multiple" data-count="5">x5</button>
                    <button class="add-multiple" data-count="10">x10</button>
                    </div>
                `;
                div.querySelectorAll('.add-multiple').forEach(button => {
                    button.addEventListener('click', (e) => {
                        e.stopPropagation();
                        addItem(item, parseFloat(button.dataset.count));
                    });
                });
                div.addEventListener('click', () => addItem(item));
                dropdown.appendChild(div);
            });
        }
    });

    function addItem(item, count = 1) {
        addDropdownItem(item, count);

        if (item.crafting) {
            Object.keys(item.crafting).forEach(key => {
                const primitive = primitives.find(p => p.title === key);
                if (primitive) {
                    addTodoItem(primitive, Math.ceil(item.crafting[key] * count));
                }
            });
        } else {
            addTodoItem(item, count);
        }
        dropdown.innerHTML = '';
        searchInput.value = '';
        savePanelsToStorage();
        closeModal();
    }

    function addDropdownItem(item, count = 1) {
        if (!activePanel) return;

        const panelContent = activePanel.querySelector('.dropdown-content');
        const existingItem = Array.from(panelContent.children).find(child => child.querySelector('img').alt.includes(item.title));

        if (existingItem) {
            const itemCount = existingItem.querySelector('.item-count');
            itemCount.textContent = parseFloat(itemCount.textContent) + count;
        } else {
            const div = document.createElement('div');
            div.className = 'item';
            div.innerHTML = `<img src="${item.image_url}" alt="${item.title}"><span class="item-count">${count}</span>`;
            panelContent.appendChild(div);
        }
    }

    function addTodoItem(item, count = 1) {
        if (!activePanel) return;

        const panelContent = activePanel.querySelector('.panel-content');
        const existingItem = Array.from(panelContent.children).find(child => child.querySelector('img').alt.includes(item.title));

        if (existingItem) {
            const itemCount = existingItem.querySelector('.item-count');
            itemCount.textContent = parseInt(itemCount.textContent) + count;
        } else {
            const div = document.createElement('div');
            div.className = 'todo-item';
            div.innerHTML = `<img src="${item.image_url}" alt="${item.title}"><span class="item-count">${count}</span>`;
            panelContent.appendChild(div);
        }
    }

    newPanelBtn.addEventListener('click', () => {
        panelCounter++;
        const panelName = panelNameInput.value.trim() || `New Panel ${panelCounter}`;
        const panel = createNewPanel(panelCounter, panelName);
        panelsContainer.appendChild(panel);
        panelNameInput.value = '';
        savePanelsToStorage();
    });

    function createNewPanel(id, name = `New Panel ${id}`) {
        const panel = document.createElement('div');
        panel.className = 'panel';
        panel.id = `panel-${id}`;
        panel.innerHTML = `
            <div class="panel-header">
                <span>${name}</span>
                <div>
                    <button class="add-item-btn">Add Item</button>
                    <button class="clear-panel-btn">Clear Items</button>
                    <button class="remove-panel-btn">Remove Panel</button>
                    <button class="up">Up</button>
                    <button class="down">Down</button>
                </div>
            </div>
            <div class="dropdown-content"></div>
            <div class="panel-content"></div>
        `;

        // Move panel up
        panel.querySelector('.up').addEventListener('click', () => {
            const previousElement = panel.previousElementSibling;
            if (previousElement) {
                panel.parentNode.insertBefore(panel, previousElement);
                savePanelsToStorage();
            }
        });

        // Move panel down
        panel.querySelector('.down').addEventListener('click', () => {
            const nextElement = panel.nextElementSibling;
            if (nextElement) {
                panel.parentNode.insertBefore(nextElement, panel);
                savePanelsToStorage();
            }
        });

        panel.querySelector('.add-item-btn').addEventListener('click', () => {
            openModal();
            activePanel = panel;
            searchInput.focus();
            dropdown.innerHTML = '';
        });

        panel.querySelector('.clear-panel-btn').addEventListener('click', () => {
            const panelContent = panel.querySelector('.panel-content');
            const dropdownContent = panel.querySelector('.dropdown-content');
            panelContent.innerHTML = '';
            dropdownContent.innerHTML = '';
            savePanelsToStorage();
        });

        panel.querySelector('.remove-panel-btn').addEventListener('click', () => {
            panelsContainer.removeChild(panel);
            if (activePanel === panel) activePanel = null;
            savePanelsToStorage();
        });

        return panel;
    }

    function savePanelsToStorage() {
        const panels = [];
        panelsContainer.querySelectorAll('.panel').forEach(panel => {
            const panelData = {
                id: panel.id,
                name: panel.querySelector('.panel-header span').textContent,
                dropdownItems: [],
                items: []
            };
            panel.querySelectorAll('.dropdown-content .item').forEach(item => {
                const img = item.querySelector('img');
                const count = item.querySelector('.item-count').textContent;
                panelData.dropdownItems.push({
                    title: img.alt,
                    image_url: img.src,
                    count: parseFloat(count)
                });
            });
            panel.querySelectorAll('.panel-content .todo-item').forEach(item => {
                const img = item.querySelector('img');
                const count = item.querySelector('.item-count').textContent;
                panelData.items.push({
                    title: img.alt,
                    image_url: img.src,
                    count: parseFloat(count)
                });
            });
            panels.push(panelData);
        });
        localStorage.setItem('panels', JSON.stringify(panels));
    }

    function loadPanelsFromStorage() {
        const panels = JSON.parse(localStorage.getItem('panels')) || [];
        panels.forEach(panelData => {
            const panel = createNewPanel(panelData.id.replace('panel-', ''), panelData.name);
            panelsContainer.appendChild(panel);
            panelData.dropdownItems.forEach(item => {
                addDropdownItemToPanel(panel, item);
            });
            panelData.items.forEach(item => {
                addTodoItemToPanel(panel, item);
            });
        });
    }

    function addDropdownItemToPanel(panel, item) {
        const panelContent = panel.querySelector('.dropdown-content');
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<img src="${item.image_url}" alt="${item.title}"><span class="item-count">${item.count}</span>`;
        panelContent.appendChild(div);
    }

    function addTodoItemToPanel(panel, item) {
        const panelContent = panel.querySelector('.panel-content');
        const div = document.createElement('div');
        div.className = 'todo-item';
        div.innerHTML = `<img src="${item.image_url}" alt="${item.title}"><span class="item-count">${item.count}</span>`;
        panelContent.appendChild(div);
    }

    function closeModal() {
        searchModal.style.display = 'none';
    }

    function openModal() {
        searchModal.style.display = 'block';
    }
});