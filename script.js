document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const dropdown = document.getElementById('dropdown');
    const todoList = document.getElementById('todo-list');
    const clearButton = document.getElementById('clear');

    let primitives = [];
    let craftables = [];

    // Function to load items from localStorage
    function loadTodoList() {
        const todoItems = JSON.parse(localStorage.getItem('todoItems')) || [];
        todoList.innerHTML = '';
        todoItems.forEach(item => {
            addOrUpdateListItem(item.title, item.quantity, item.image_url);
        });
    }

    // Fetch the JSON data
    fetch('data/primitives.json')
        .then(response => response.json())
        .then(data => {
            primitives = data;
            console.log('Primitives loaded:', primitives);
        })
        .catch(error => console.error('Error loading primitives:', error));

    fetch('data/ingredients.json')
        .then(response => response.json())
        .then(data => {
            craftables = data;
            console.log('Craftables loaded:', craftables);
        })
        .catch(error => console.error('Error loading craftables:', error));

    // Load existing items from localStorage on page load
    loadTodoList();

    searchInput.addEventListener('input', () => {
        const searchValue = searchInput.value.toLowerCase();
        dropdown.innerHTML = '';
        if (searchValue) {
            const matchedPrimitives = primitives.filter(item => item.title.toLowerCase().includes(searchValue));
            const matchedCraftables = craftables.filter(item => item.title.toLowerCase().includes(searchValue));

            if (matchedPrimitives.length > 0 || matchedCraftables.length > 0) {
                [...matchedPrimitives, ...matchedCraftables].forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'dropdown-item';
                    div.innerHTML = `
                        <img src="${item.image_url}" alt="${item.title}"> ${item.title}
                        <button class="add-button" data-title="${item.title}" data-quantity="1">1x</button>
                        <button class="add-button" data-title="${item.title}" data-quantity="2">2x</button>
                        <button class="add-button" data-title="${item.title}" data-quantity="5">5x</button>
                        <button class="add-button" data-title="${item.title}" data-quantity="10">10x</button>
                    `;
                    dropdown.appendChild(div);
                });

                dropdown.style.display = 'block';
                adjustDropdownPosition();
            } else {
                dropdown.style.display = 'none';
            }
        } else {
            dropdown.style.display = 'none';
        }
    });

    dropdown.addEventListener('click', (event) => {
        if (event.target.classList.contains('add-button')) {
            const title = event.target.dataset.title;
            const quantity = parseInt(event.target.dataset.quantity, 10);
            const item = primitives.find(p => p.title === title) || craftables.find(c => c.title === title);
            if (item) {
                addItemToList(item, quantity);
                saveTodoList(); // Save the updated todo list to localStorage
            }
            dropdown.innerHTML = '';
            dropdown.style.display = 'none';
            searchInput.value = '';
        }
    });

    todoList.addEventListener('click', (event) => {
        if (event.target.classList.contains('increase-quantity')) {
            const li = event.target.closest('li');
            const title = li.dataset.title;
            updateQuantity(title, 1);
            saveTodoList(); // Save the updated todo list to localStorage
        } else if (event.target.classList.contains('decrease-quantity')) {
            const li = event.target.closest('li');
            const title = li.dataset.title;
            updateQuantity(title, -1);
            saveTodoList(); // Save the updated todo list to localStorage
        }
    });

    function addItemToList(item, quantity = 1) {
        if (item.crafting) {
            Object.keys(item.crafting).forEach(ingredient => {
                const primitive = primitives.find(p => p.title === ingredient);
                if (primitive) {
                    addOrUpdateListItem(primitive.title, item.crafting[ingredient] * quantity, primitive.image_url);
                } else {
                    console.error('Primitive not found:', ingredient);
                }
            });
        } else {
            addOrUpdateListItem(item.title, quantity, item.image_url);
        }
    }

    function addOrUpdateListItem(title, quantity = 1, imageUrl) {
        const existingItem = [...todoList.children].find(li => li.dataset.title === title);

        if (existingItem) {
            const existingQuantity = parseInt(existingItem.dataset.quantity, 10);
            const newQuantity = existingQuantity + quantity;
            existingItem.dataset.quantity = newQuantity;
            existingItem.querySelector('.quantity').textContent = `x${newQuantity}`;
        } else {
            const li = document.createElement('li');
            li.className = 'todo-item';
            li.dataset.title = title;
            li.dataset.quantity = quantity;
            li.innerHTML = `
                <img src="${imageUrl}" alt="${title}">
                ${title} <span class="quantity">x${quantity}</span>
                <button class="increase-quantity">+</button>
                <button class="decrease-quantity">-</button>
            `;
            todoList.appendChild(li);
        }
    }

    function updateQuantity(title, change) {
        const item = [...todoList.children].find(li => li.dataset.title === title);
        if (item) {
            const currentQuantity = parseInt(item.dataset.quantity, 10);
            const newQuantity = currentQuantity + change;
            if (newQuantity > 0) {
                item.dataset.quantity = newQuantity;
                item.querySelector('.quantity').textContent = `x${newQuantity}`;
            } else {
                item.remove();
            }
        }
    }

    function adjustDropdownPosition() {
        const rect = searchInput.getBoundingClientRect();
        dropdown.style.top = `${rect.bottom}px`;
        dropdown.style.left = `${rect.left}px`;
        dropdown.style.width = `${rect.width}px`;
    }

    // Save current todo list to localStorage
    function saveTodoList() {
        const todoItems = [...todoList.children].map(li => ({
            title: li.dataset.title,
            quantity: parseInt(li.dataset.quantity, 10),
            image_url: findItemByTitle(li.dataset.title)?.image_url || ''
        }));
        localStorage.setItem('todoItems', JSON.stringify(todoItems));
    }

    clearButton.addEventListener('click', () => {
        todoList.innerHTML = '';
        localStorage.removeItem('todoItems'); // Remove todoItems from localStorage when clearing
    });

    // Helper function to find item by title in primitives or craftables
    function findItemByTitle(title) {
        return primitives.find(p => p.title === title) || craftables.find(c => c.title === title);
    }
});