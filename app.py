from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
EXCEL_FILE = 'حي الزمالك.xlsx'
STATIC_FOLDER = '.'  # Current directory for HTML files

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Valid credentials
VALID_CREDENTIALS = {
    'admin': 'admin123',
    'ثروت_شرقاوى': 'president2024',
    'شرف_اسماعيل': 'vice2024',
    'محمد_مسعود': 'finance2024',
    'مليسة_مصطفى': 'member2024',
    'نيفين_الديباغ': 'secretary2024'
}

def init_excel_file():
    """Initialize Excel file with sample data if it doesn't exist"""
    if not os.path.exists(EXCEL_FILE):
        # البيانات الجديدة بالأعمدة المطلوبة
        sample_data = {
            'رقم م': [1, 2, 3],
            'اسم العضو': ['أحمد محمد علي', 'فاطمة حسن محمود', 'محمد عبد الرحمن'],
            'عضوية': [1001, 1002, 1003],
            'شقة': [5, 12, 8],
            'عمارة': [1, 2, 1],
            'حي': ['الزمالك الشرقي', 'الزمالك الغربي', 'الزمالك الشمالي'],
            'المبلغ المدفوع': [5000.00, 7500.50, 6200.25],
            'تاريخ التسجيل': ['2024-01-15', '2024-02-20', '2024-03-10']
        }
        
        df = pd.DataFrame(sample_data)
        
        try:
            # إنشاء Excel writer مع تنسيق
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='بيانات الأعضاء')
                
                # الحصول على الـ worksheet
                worksheet = writer.sheets['بيانات الأعضاء']
                
                # ضبط عرض الأعمدة
                column_widths = {
                    'A': 10,  # رقم م
                    'B': 25,  # اسم العضو
                    'C': 12,  # عضوية
                    'D': 10,  # شقة
                    'E': 10,  # عمارة
                    'F': 20,  # حي
                    'G': 18,  # المبلغ المدفوع
                    'H': 20   # تاريخ التسجيل
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
            
            logger.info(f"✅ تم إنشاء ملف '{EXCEL_FILE}' بنجاح")
        
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء ملف Excel: {e}")

def read_excel():
    """Read data from Excel file"""
    try:
        if not os.path.exists(EXCEL_FILE):
            init_excel_file()
        
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl', sheet_name='بيانات الأعضاء')
        data = df.to_dict('records')
        
        # تنظيف البيانات
        for record in data:
            for key, value in record.items():
                if pd.isna(value):
                    if key == 'المبلغ المدفوع':
                        record[key] = 0.0
                    else:
                        record[key] = ''
                else:
                    # تحويل المبلغ لـ float
                    if key == 'المبلغ المدفوع':
                        try:
                            record[key] = float(value)
                        except:
                            record[key] = 0.0
                    # تحويل الأرقام للأعمدة المطلوبة
                    elif key in ['رقم م', 'عضوية', 'شقة', 'عمارة']:
                        try:
                            record[key] = int(float(value))
                        except:
                            record[key] = 0
                    else:
                        record[key] = str(value)
        
        return data
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة Excel: {e}")
        return []

def write_excel(data):
    """Write data to Excel file"""
    try:
        if not data:
            logger.warning("⚠️ لا توجد بيانات للكتابة")
            return False
        
        df = pd.DataFrame(data)
        
        # التأكد من ترتيب الأعمدة
        columns_order = ['رقم م', 'اسم العضو', 'عضوية', 'شقة', 'عمارة', 'حي', 'المبلغ المدفوع', 'تاريخ التسجيل']
        df = df.reindex(columns=columns_order)
        
        # كتابة البيانات مع التنسيق
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='بيانات الأعضاء')
            
            worksheet = writer.sheets['بيانات الأعضاء']
            
            # ضبط عرض الأعمدة
            column_widths = {
                'A': 10, 'B': 25, 'C': 12, 'D': 10, 
                'E': 10, 'F': 20, 'G': 18, 'H': 20
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        logger.info(f"✅ تم حفظ البيانات في '{EXCEL_FILE}'")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في كتابة Excel: {e}")
        return False

def get_next_id():
    """Get next available ID"""
    data = read_excel()
    if not data:
        return 1
    
    max_id = max([int(record.get('رقم م', 0)) for record in data])
    return max_id + 1

# Routes for serving HTML files
@app.route('/')
def serve_login():
    """Serve login page"""
    try:
        return send_from_directory(STATIC_FOLDER, 'login.html')
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل صفحة تسجيل الدخول: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500

@app.route('/dashboard.html')
def serve_dashboard():
    """Serve dashboard page"""
    try:
        return send_from_directory(STATIC_FOLDER, 'dashboard.html')
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل لوحة التحكم: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500

@app.route('/login.html')
def serve_login_explicit():
    """Serve login page explicitly"""
    try:
        return send_from_directory(STATIC_FOLDER, 'login.html')
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل صفحة تسجيل الدخول: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    try:
        return send_from_directory(STATIC_FOLDER, path)
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل الملف: {path} - {e}")
        return jsonify({'error': 'الملف غير موجود'}), 404

# API Routes
@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'البيانات غير صالحة'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'الرجاء إدخال اسم المستخدم وكلمة المرور'
            }), 400
        
        if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
            logger.info(f"✅ تسجيل دخول ناجح: {username}")
            return jsonify({
                'success': True,
                'message': 'تم تسجيل الدخول بنجاح',
                'username': username
            })
        else:
            logger.warning(f"❌ محاولة تسجيل دخول فاشلة: {username}")
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
    
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل الدخول: {e}")
        return jsonify({
            'success': False,
            'message': 'خطأ في الخادم'
        }), 500

@app.route('/api/members', methods=['GET'])
def get_all_members():
    """Get all members"""
    try:
        members = read_excel()
        logger.info(f"✅ تم جلب {len(members)} عضو")
        return jsonify({
            'success': True,
            'data': members,
            'count': len(members)
        })
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الأعضاء: {e}")
        return jsonify({
            'success': False,
            'message': 'خطأ في قراءة البيانات'
        }), 500

@app.route('/api/members/search', methods=['GET'])
def search_members():
    """Search for members by name"""
    try:
        search_term = request.args.get('name', '').strip().lower()
        
        if not search_term:
            return jsonify({
                'success': False,
                'message': 'الرجاء إدخال اسم للبحث'
            }), 400
        
        members = read_excel()
        found_members = []
        
        for member in members:
            if search_term in str(member.get('اسم العضو', '')).lower():
                found_members.append(member)
        
        logger.info(f"🔍 البحث عن '{search_term}' - تم العثور على {len(found_members)} نتيجة")
        return jsonify({
            'success': True,
            'data': found_members,
            'count': len(found_members)
        })
    
    except Exception as e:
        logger.error(f"❌ خطأ في البحث: {e}")
        return jsonify({
            'success': False,
            'message': 'خطأ في البحث'
        }), 500

@app.route('/api/members', methods=['POST'])
def add_member():
    """Add new member"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'البيانات غير صالحة'
            }), 400
        
        # التحقق من الحقول المطلوبة
        required_fields = ['اسم العضو', 'عضوية', 'شقة', 'عمارة', 'حي']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'الحقل "{field}" مطلوب'
                }), 400
        
        members = read_excel()
        next_id = get_next_id()
        
        new_member = {
            'رقم م': next_id,
            'اسم العضو': data.get('اسم العضو', '').strip(),
            'عضوية': int(data.get('عضوية', 0)),
            'شقة': int(data.get('شقة', 0)),
            'عمارة': int(data.get('عمارة', 0)),
            'حي': data.get('حي', '').strip(),
            'المبلغ المدفوع': float(data.get('المبلغ المدفوع', 0.0)),
            'تاريخ التسجيل': datetime.now().strftime('%Y-%m-%d')
        }
        
        members.append(new_member)
        
        if write_excel(members):
            logger.info(f"✅ تم إضافة عضو جديد: {new_member['اسم العضو']}")
            return jsonify({
                'success': True,
                'message': 'تم إضافة العضو بنجاح',
                'data': new_member
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطأ في حفظ البيانات'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ خطأ في إضافة عضو: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ في إضافة العضو: {str(e)}'
        }), 500

@app.route('/api/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """Update existing member"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'البيانات غير صالحة'
            }), 400
        
        members = read_excel()
        
        member_index = None
        for i, member in enumerate(members):
            if int(member.get('رقم م', 0)) == member_id:
                member_index = i
                break
        
        if member_index is None:
            return jsonify({
                'success': False,
                'message': 'العضو غير موجود'
            }), 404
        
        # تحديث البيانات
        old_name = members[member_index]['اسم العضو']
        members[member_index].update({
            'اسم العضو': data.get('اسم العضو', members[member_index]['اسم العضو']).strip(),
            'عضوية': int(data.get('عضوية', members[member_index]['عضوية'])),
            'شقة': int(data.get('شقة', members[member_index]['شقة'])),
            'عمارة': int(data.get('عمارة', members[member_index]['عمارة'])),
            'حي': data.get('حي', members[member_index]['حي']).strip(),
            'المبلغ المدفوع': float(data.get('المبلغ المدفوع', members[member_index]['المبلغ المدفوع']))
        })
        
        if write_excel(members):
            logger.info(f"✅ تم تحديث بيانات العضو: {old_name}")
            return jsonify({
                'success': True,
                'message': 'تم تحديث بيانات العضو بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطأ في حفظ البيانات'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث عضو: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ في تحديث العضو: {str(e)}'
        }), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Delete member"""
    try:
        members = read_excel()
        
        member_found = False
        deleted_member_name = ""
        
        for i, member in enumerate(members):
            if int(member.get('رقم م', 0)) == member_id:
                deleted_member_name = member.get('اسم العضو', 'Unknown')
                members.pop(i)
                member_found = True
                break
        
        if not member_found:
            return jsonify({
                'success': False,
                'message': 'العضو غير موجود'
            }), 404
        
        if write_excel(members):
            logger.info(f"🗑️ تم حذف العضو: {deleted_member_name}")
            return jsonify({
                'success': True,
                'message': 'تم حذف العضو بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطأ في حفظ البيانات'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ خطأ في حذف عضو: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ في حذف العضو: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get database statistics"""
    try:
        members = read_excel()
        
        stats = {
            'total_members': len(members),
            'members_with_email': len([m for m in members if m.get('البريد الإلكتروني', '').strip()]),
            'total_amount': sum([float(m.get('المبلغ المدفوع', 0)) for m in members]),
            'districts': len(set([m.get('حي', '') for m in members if m.get('حي', '').strip()]))
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الإحصائيات: {e}")
        return jsonify({
            'success': False,
            'message': 'خطأ في جلب الإحصائيات'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'الصفحة غير موجودة'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'خطأ داخلي في الخادم'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'الطريقة غير مسموحة'
    }), 405

# Health check route
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'الخادم يعمل بشكل طبيعي',
        'excel_file_exists': os.path.exists(EXCEL_FILE)
    })

if __name__ == '__main__':
    # Initialize Excel file
    init_excel_file()
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Print startup information
    print("=" * 60)
    print("🚀 Flask API Server - نظام إدارة الشقق السكنية")
    print(f"📊 ملف البيانات: {EXCEL_FILE}")
    print(f"🌐 المنفذ: {port}")
    print("👥 المستخدمون المسموح لهم:")
    for username in VALID_CREDENTIALS.keys():
        print(f"   - {username}")
    print("🔗 API Endpoints:")
    print("   - POST /api/login")
    print("   - GET  /api/members")
    print("   - POST /api/members")
    print("   - PUT  /api/members/<id>")
    print("   - DELETE /api/members/<id>")
    print("   - GET  /api/members/search")
    print("   - GET  /api/stats")
    print("   - GET  /health")
    print("=" * 60)
    
    # Run the server
    app.run(
        debug=False,  # Set to False for production
        host='0.0.0.0',  # Listen on all interfaces
        port=port  # Use Railway's assigned port
    )