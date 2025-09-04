const API_BASE = 'http://localhost:5000/api';
let membersData = [];
let searchTimeout = null;

window.addEventListener('load', function() {
    if (!localStorage.getItem('isLoggedIn')) {
        window.location.href = 'login.html';
        return;
    }
    
    const username = localStorage.getItem('username');
    document.getElementById('userInfo').textContent = `مرحباً ${username}`;
    
    loadMembers();
});

// API Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw new Error('خطأ في الاتصال بالخادم');
    }
}

// Load all members
async function loadMembers() {
    try {
        const result = await apiCall('/members');
        if (result.success) {
            membersData = result.data;
        }
    } catch (error) {
        showMessage('crud-messages', 'error', error.message);
    }
}

// Show/Hide functions
function showSection(sectionId) {
    document.getElementById('main-menu').style.display = 'none';
    
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    document.getElementById(sectionId).classList.add('active');
    
    if (sectionId === 'crud-section') {
        loadMembers();
    }
}

function showMainMenu() {
    document.getElementById('main-menu').style.display = 'block';
    
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    hideAllForms();
}

function showForm(formId) {
    hideAllForms();
    document.getElementById(formId).classList.add('active');
}

function hideAllForms() {
    const forms = document.querySelectorAll('.form-container');
    forms.forEach(form => form.classList.remove('active'));
    
    document.getElementById('members-table').style.display = 'none';
    clearMessages();
    
    // تنظيف الـ search
    clearSelectedMember('edit');
    clearSelectedMember('delete');
    hideSearchResults('edit');
    hideSearchResults('delete');
}

// Member Search Functions
function searchForMember(type) {
    const searchInput = document.getElementById(`${type}-search-input`);
    const searchTerm = searchInput.value.trim();
    
    // مسح الـ timeout السابق
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // إخفاء النتائج إذا كان البحث فارغ
    if (!searchTerm) {
        hideSearchResults(type);
        return;
    }
    
    // تأخير البحث لتجنب الكثير من الطلبات
    searchTimeout = setTimeout(() => {
        performMemberSearch(searchTerm, type);
    }, 300);
}

function performMemberSearch(searchTerm, type) {
    // فلترة الأعضاء
    const filteredMembers = membersData.filter(member => {
        const name = member['اسم العضو'].toLowerCase();
        const membership = member['عضوية'].toString();
        const searchLower = searchTerm.toLowerCase();
        
        return name.includes(searchLower) || membership.includes(searchLower);
    });
    
    // عرض النتائج
    displaySearchResults(filteredMembers, type);
}

function displaySearchResults(results, type) {
    const resultsContainer = document.getElementById(`${type}-search-results`);
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">لم يتم العثور على أي نتائج</div>';
        resultsContainer.style.display = 'block';
        return;
    }
    
    let html = '';
    results.forEach(member => {
        html += `
            <div class="search-result-item" onclick="selectMember(${member['رقم م']}, '${type}')">
                <div class="search-result-name">${member['اسم العضو']}</div>
                <div class="search-result-details">
                    عضوية: ${member['عضوية']} | شقة: ${member['شقة']}/${member['عمارة']} | ${member['حي']}
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
}

function selectMember(memberId, type) {
    const member = membersData.find(m => m['رقم م'] == memberId);
    
    if (!member) return;
    
    // حفظ ID العضو
    document.getElementById(`${type}-member-id`).value = memberId;
    
    // عرض العضو المختار
    const selectedContainer = document.getElementById(`${type}-selected-member`);
    const selectedInfo = document.getElementById(`${type}-selected-info`);
    
    selectedInfo.textContent = `${member['اسم العضو']} - عضوية ${member['عضوية']} - شقة ${member['شقة']}/${member['عمارة']}`;
    selectedContainer.style.display = 'flex';
    
    // إخفاء نتائج البحث
    hideSearchResults(type);
    
    // مسح حقل البحث
    document.getElementById(`${type}-search-input`).value = '';
    
    // إذا كان في التعديل، تحميل بيانات العضو
    if (type === 'edit') {
        loadMemberDataForEdit(member);
        document.getElementById('edit-form-fields').style.display = 'block';
    }
    
    // إذا كان في الحذف، إظهار أزرار الحذف
    if (type === 'delete') {
        document.getElementById('delete-form-actions').style.display = 'flex';
    }
}

function loadMemberDataForEdit(member) {
    document.getElementById('edit-name').value = member['اسم العضو'] || '';
    document.getElementById('edit-membership').value = member['عضوية'] || '';
    document.getElementById('edit-apartment').value = member['شقة'] || '';
    document.getElementById('edit-building').value = member['عمارة'] || '';
    document.getElementById('edit-district').value = member['حي'] || '';
    document.getElementById('edit-amount').value = member['المبلغ المدفوع'] || '';
}

function clearSelectedMember(type) {
    document.getElementById(`${type}-member-id`).value = '';
    document.getElementById(`${type}-selected-member`).style.display = 'none';
    document.getElementById(`${type}-search-input`).value = '';
    
    if (type === 'edit') {
        document.getElementById('edit-form-fields').style.display = 'none';
        // مسح الحقول
        document.getElementById('edit-name').value = '';
        document.getElementById('edit-membership').value = '';
        document.getElementById('edit-apartment').value = '';
        document.getElementById('edit-building').value = '';
        document.getElementById('edit-district').value = '';
        document.getElementById('edit-amount').value = '';
    }
    
    if (type === 'delete') {
        document.getElementById('delete-form-actions').style.display = 'none';
    }
}

function hideSearchResults(type) {
    const resultsElement = document.getElementById(`${type}-search-results`);
    if (resultsElement) {
        resultsElement.style.display = 'none';
    }
}

// CRUD Operations
async function addMember(event) {
    event.preventDefault();
    
    const memberData = {
        'اسم العضو': document.getElementById('add-name').value.trim(),
        'عضوية': parseInt(document.getElementById('add-membership').value) || 0,
        'شقة': parseInt(document.getElementById('add-apartment').value) || 0,
        'عمارة': parseInt(document.getElementById('add-building').value) || 0,
        'حي': document.getElementById('add-district').value.trim(),
        'المبلغ المدفوع': parseFloat(document.getElementById('add-amount').value) || 0.0
    };
    
    try {
        const result = await apiCall('/members', 'POST', memberData);
        
        if (result.success) {
            showMessage('crud-messages', 'success', result.message);
            event.target.reset();
            await loadMembers();
            hideAllForms();
        } else {
            showMessage('crud-messages', 'error', result.message);
        }
    } catch (error) {
        showMessage('crud-messages', 'error', error.message);
    }
}

async function editMember(event) {
    event.preventDefault();
    
    const memberId = parseInt(document.getElementById('edit-member-id').value);
    
    if (!memberId) {
        showMessage('crud-messages', 'error', 'الرجاء اختيار عضو للتعديل');
        return;
    }
    
    const memberData = {
        'اسم العضو': document.getElementById('edit-name').value.trim(),
        'عضوية': parseInt(document.getElementById('edit-membership').value) || 0,
        'شقة': parseInt(document.getElementById('edit-apartment').value) || 0,
        'عمارة': parseInt(document.getElementById('edit-building').value) || 0,
        'حي': document.getElementById('edit-district').value.trim(),
        'المبلغ المدفوع': parseFloat(document.getElementById('edit-amount').value) || 0.0
    };
    
    try {
        const result = await apiCall(`/members/${memberId}`, 'PUT', memberData);
        
        if (result.success) {
            showMessage('crud-messages', 'success', result.message);
            await loadMembers();
            hideAllForms();
        } else {
            showMessage('crud-messages', 'error', result.message);
        }
    } catch (error) {
        showMessage('crud-messages', 'error', error.message);
    }
}

async function deleteMember(event) {
    event.preventDefault();
    
    const memberId = parseInt(document.getElementById('delete-member-id').value);
    
    if (!memberId) {
        showMessage('crud-messages', 'error', 'الرجاء اختيار عضو للحذف');
        return;
    }
    
    const member = membersData.find(m => m['رقم م'] == memberId);
    
    if (!member) {
        showMessage('crud-messages', 'error', 'العضو غير موجود');
        return;
    }
    
    if (confirm(`هل أنت متأكد من حذف العضو: ${member['اسم العضو']}؟`)) {
        try {
            const result = await apiCall(`/members/${memberId}`, 'DELETE');
            
            if (result.success) {
                showMessage('crud-messages', 'success', result.message);
                await loadMembers();
                hideAllForms();
            } else {
                showMessage('crud-messages', 'error', result.message);
            }
        } catch (error) {
            showMessage('crud-messages', 'error', error.message);
        }
    }
}

async function viewAllMembers() {
    hideAllForms();
    
    try {
        await loadMembers();
        
        let tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>رقم م</th>
                        <th>اسم العضو</th>
                        <th>عضوية</th>
                        <th>شقة</th>
                        <th>عمارة</th>
                        <th>الحي</th>
                        <th>المبلغ المدفوع</th>
                        <th>تاريخ التسجيل</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        membersData.forEach(member => {
            const amount = parseFloat(member['المبلغ المدفوع']) || 0;
            const formattedAmount = new Intl.NumberFormat('ar-EG', {
                style: 'currency',
                currency: 'EGP'
            }).format(amount);
            
            const date = new Date(member['تاريخ التسجيل']);
            const formattedDate = date.toLocaleDateString('ar-EG', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            tableHTML += `
                <tr>
                    <td>${member['رقم م']}</td>
                    <td>${member['اسم العضو']}</td>
                    <td>${member['عضوية']}</td>
                    <td>${member['شقة']}</td>
                    <td>${member['عمارة']}</td>
                    <td>${member['حي']}</td>
                    <td class="amount-cell">${formattedAmount}</td>
                    <td class="date-cell">${formattedDate}</td>
                </tr>
            `;
        });
        
        tableHTML += '</tbody></table>';
        
        document.getElementById('table-container').innerHTML = tableHTML;
        document.getElementById('members-table').style.display = 'block';
        
    } catch (error) {
        showMessage('crud-messages', 'error', error.message);
    }
}

async function searchMember() {
    const searchTerm = document.getElementById('search-input').value.trim();
    
    if (!searchTerm) {
        showMessage('search-messages', 'error', 'الرجاء إدخال اسم للبحث');
        return;
    }
    
    try {
        const result = await apiCall(`/members/search?name=${encodeURIComponent(searchTerm)}`);
        
        if (result.success && result.data.length > 0) {
            let tableHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>رقم م</th>
                            <th>اسم العضو</th>
                            <th>عضوية</th>
                            <th>شقة</th>
                            <th>عمارة</th>
                            <th>الحي</th>
                            <th>المبلغ المدفوع</th>
                            <th>تاريخ التسجيل</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            result.data.forEach(member => {
                const amount = parseFloat(member['المبلغ المدفوع']) || 0;
                const formattedAmount = new Intl.NumberFormat('ar-EG', {
                    style: 'currency',
                    currency: 'EGP'
                }).format(amount);
                
                const date = new Date(member['تاريخ التسجيل']);
                const formattedDate = date.toLocaleDateString('ar-EG', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                
                tableHTML += `
                    <tr>
                        <td>${member['رقم م']}</td>
                        <td>${member['اسم العضو']}</td>
                        <td>${member['عضوية']}</td>
                        <td>${member['شقة']}</td>
                        <td>${member['عمارة']}</td>
                        <td>${member['حي']}</td>
                        <td class="amount-cell">${formattedAmount}</td>
                        <td class="date-cell">${formattedDate}</td>
                    </tr>
                `;
            });
            
            tableHTML += '</tbody></table>';
            
            document.getElementById('search-table-container').innerHTML = tableHTML;
            document.getElementById('search-result').style.display = 'block';
            
            showMessage('search-messages', 'success', `تم العثور على ${result.count} نتيجة`);
            
        } else {
            document.getElementById('search-result').style.display = 'none';
            showMessage('search-messages', 'error', 'لم يتم العثور على أي نتائج');
        }
        
    } catch (error) {
        showMessage('search-messages', 'error', error.message);
    }
}

// Utility Functions
function showMessage(containerId, type, message) {
    const container = document.getElementById(containerId);
    const messageClass = type === 'success' ? 'success-message' : 'error-message';
    
    container.innerHTML = `<div class="${messageClass}">${message}</div>`;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

function clearMessages() {
    document.getElementById('crud-messages').innerHTML = '';
    document.getElementById('search-messages').innerHTML = '';
}

function logout() {
    if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Search on Enter key
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                searchMember();
            }
        });
    }
});

// إغلاق نتائج البحث عند النقر خارجها
document.addEventListener('click', function(event) {
    const editSearch = document.getElementById('edit-search-input');
    const deleteSearch = document.getElementById('delete-search-input');
    const editResults = document.getElementById('edit-search-results');
    const deleteResults = document.getElementById('delete-search-results');
    
    // للتعديل
    if (editSearch && editResults && 
        !editSearch.contains(event.target) && 
        !editResults.contains(event.target)) {
        hideSearchResults('edit');
    }
    
    // للحذف
    if (deleteSearch && deleteResults && 
        !deleteSearch.contains(event.target) && 
        !deleteResults.contains(event.target)) {
        hideSearchResults('delete');
    }
});