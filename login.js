document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const loading = document.getElementById('loading');
    
    // إخفاء الرسائل السابقة
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    loading.style.display = 'block';

    // التحقق من البيانات
    if (!username || !password) {
        loading.style.display = 'none';
        errorMessage.textContent = 'الرجاء إدخال اسم المستخدم وكلمة المرور';
        errorMessage.style.display = 'block';
        return;
    }

    // إرسال البيانات للسيرفر
    fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        
        if (data.success) {
            // حفظ بيانات الجلسة
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('username', data.username);
            localStorage.setItem('loginTime', new Date().toISOString());
            
            successMessage.textContent = 'تم تسجيل الدخول بنجاح!';
            successMessage.style.display = 'block';
            
            // الانتقال للصفحة الرئيسية
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            errorMessage.textContent = data.message || 'خطأ في اسم المستخدم أو كلمة المرور';
            errorMessage.style.display = 'block';
        }
    })
    .catch(error => {
        loading.style.display = 'none';
        errorMessage.textContent = 'حدث خطأ في الاتصال بالخادم. تأكد من تشغيل الخادم أولاً.';
        errorMessage.style.display = 'block';
        console.error('Login error:', error);
    });
});

// التحقق من تسجيل الدخول المسبق
window.addEventListener('load', function() {
    if (localStorage.getItem('isLoggedIn') === 'true') {
        window.location.href = 'dashboard.html';
    }
});