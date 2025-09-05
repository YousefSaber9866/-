from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///zamalek.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Valid credentials
VALID_CREDENTIALS = {
    'admin': 'admin123',
    'ثروت_شرقاوى': 'president2024',
    'شرف_اسماعيل': 'vice2024',
    'محمد_مسعود': 'finance2024',
    'مليسة_مصطفى': 'member2024',
    'نيفين_الديباغ': 'secretary2024'
}

# Database Model
class Member(db.Model):
    __tablename__ = 'members'
    
    رقم_م = db.Column('رقم_م', db.Integer, primary_key=True, autoincrement=True)
    اسم_العضو = db.Column('اسم_العضو', db.String(255), nullable=False)
    عضوية = db.Column('عضوية', db.Integer, nullable=False)
    شقة = db.Column('شقة', db.Integer, nullable=False)
    عمارة = db.Column('عمارة', db.Integer, nullable=False)
    حي = db.Column('حي', db.String(255), nullable=False)
    المبلغ_المدفوع = db.Column('المبلغ_المدفوع', db.Float, default=0.0)
    تاريخ_التسجيل = db.Column('تاريخ_التسجيل', db.Date, default=datetime.now().date)
    
    def to_dict(self):
        return {
            'رقم م': self.رقم_م,
            'اسم العضو': self.اسم_العضو,
            'عضوية': self.عضوية,
            'شقة': self.شقة,
            'عمارة': self.عمارة,
            'حي': self.حي,
            'المبلغ المدفوع': float(self.المبلغ_المدفوع) if self.المبلغ_المدفوع else 0.0,
            'تاريخ التسجيل': self.تاريخ_التسجيل.strftime('%Y-%m-%d') if self.تاريخ_التسجيل else ''
        }

def init_database():
    """Initialize database and create sample data"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Check if we have any data
            if Member.query.count() == 0:
                # Create sample data
                sample_members = [
                    Member(
                        اسم_العضو='أحمد محمد علي',
                        عضوية=1001,
                        شقة=5,
                        عمارة=1,
                        حي='الزمالك الشرقي',
                        المبلغ_المدفوع=5000.00,
                        تاريخ_التسجيل=datetime.strptime('2024-01-15', '%Y-%m-%d').date()
                    ),
                    Member(
                        اسم_العضو='فاطمة حسن محمود',
                        عضوية=1002,
                        شقة=12,
                        عمارة=2,
                        حي='الزمالك الغربي',
                        المبلغ_المدفوع=7500.50,
                        تاريخ_التسجيل=datetime.strptime('2024-02-20', '%Y-%m-%d').date()
                    ),
                    Member(
                        اسم_العضو='محمد عبد الرحمن',
                        عضوية=1003,
                        شقة=8,
                        عمارة=1,
                        حي='الزمالك الشمالي',
                        المبلغ_المدفوع=6200.25,
                        تاريخ_التسجيل=datetime.strptime('2024-03-10', '%Y-%m-%d').date()
                    )
                ]
                
                for member in sample_members:
                    db.session.add(member)
                
                db.session.commit()
                logger.info(f"✅ تم إنشاء قاعدة البيانات مع {len(sample_members)} عضو نموذجي")
            else:
                logger.info(f"✅ قاعدة البيانات موجودة مع {Member.query.count()} عضو")
                
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")

# Routes for serving HTML files
@app.route('/')
def serve_login():
    """Serve login page"""
    try:
        return send_from_directory('.', 'login.html')
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل صفحة تسجيل الدخول: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500

@app.route('/dashboard.html')
def serve_dashboard():
    """Serve dashboard page"""
    try:
        return send_from_directory('.', 'dashboard.html')
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل لوحة التحكم: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500

@app.route('/login.html')
def serve_login_explicit():
    """Serve login page explicitly"""
    try:
        return send_from_directory('.', 'login.html')
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل صفحة تسجيل الدخول: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    try:
        return send_from_directory('.', path)
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
        members = Member.query.all()
        members_list = [member.to_dict() for member in members]
        
        logger.info(f"✅ تم جلب {len(members_list)} عضو")
        return jsonify({
            'success': True,
            'data': members_list,
            'count': len(members_list)
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
        search_term = request.args.get('name', '').strip()
        
        if not search_term:
            return jsonify({
                'success': False,
                'message': 'الرجاء إدخال اسم للبحث'
            }), 400
        
        # Search in name field
        members = Member.query.filter(
            Member.اسم_العضو.ilike(f'%{search_term}%')
        ).all()
        
        members_list = [member.to_dict() for member in members]
        
        logger.info(f"🔍 البحث عن '{search_term}' - تم العثور على {len(members_list)} نتيجة")
        return jsonify({
            'success': True,
            'data': members_list,
            'count': len(members_list)
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
        
        # Check if membership number already exists
        existing_member = Member.query.filter_by(عضوية=int(data.get('عضوية'))).first()
        if existing_member:
            return jsonify({
                'success': False,
                'message': 'رقم العضوية موجود مسبقاً'
            }), 400
        
        new_member = Member(
            اسم_العضو=data.get('اسم العضو', '').strip(),
            عضوية=int(data.get('عضوية', 0)),
            شقة=int(data.get('شقة', 0)),
            عمارة=int(data.get('عمارة', 0)),
            حي=data.get('حي', '').strip(),
            المبلغ_المدفوع=float(data.get('المبلغ المدفوع', 0.0)),
            تاريخ_التسجيل=datetime.now().date()
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        logger.info(f"✅ تم إضافة عضو جديد: {new_member.اسم_العضو}")
        return jsonify({
            'success': True,
            'message': 'تم إضافة العضو بنجاح',
            'data': new_member.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
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
        
        member = Member.query.get(member_id)
        if not member:
            return jsonify({
                'success': False,
                'message': 'العضو غير موجود'
            }), 404
        
        # Check if new membership number conflicts with another member
        new_membership = int(data.get('عضوية', member.عضوية))
        if new_membership != member.عضوية:
            existing_member = Member.query.filter_by(عضوية=new_membership).first()
            if existing_member:
                return jsonify({
                    'success': False,
                    'message': 'رقم العضوية موجود مسبقاً'
                }), 400
        
        # Update member data
        old_name = member.اسم_العضو
        member.اسم_العضو = data.get('اسم العضو', member.اسم_العضو).strip()
        member.عضوية = new_membership
        member.شقة = int(data.get('شقة', member.شقة))
        member.عمارة = int(data.get('عمارة', member.عمارة))
        member.حي = data.get('حي', member.حي).strip()
        member.المبلغ_المدفوع = float(data.get('المبلغ المدفوع', member.المبلغ_المدفوع))
        
        db.session.commit()
        
        logger.info(f"✅ تم تحديث بيانات العضو: {old_name}")
        return jsonify({
            'success': True,
            'message': 'تم تحديث بيانات العضو بنجاح'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ في تحديث عضو: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ في تحديث العضو: {str(e)}'
        }), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Delete member"""
    try:
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({
                'success': False,
                'message': 'العضو غير موجود'
            }), 404
        
        deleted_member_name = member.اسم_العضو
        db.session.delete(member)
        db.session.commit()
        
        logger.info(f"🗑️ تم حذف العضو: {deleted_member_name}")
        return jsonify({
            'success': True,
            'message': 'تم حذف العضو بنجاح'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ في حذف عضو: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ في حذف العضو: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get database statistics"""
    try:
        total_members = Member.query.count()
        total_amount = db.session.query(db.func.sum(Member.المبلغ_المدفوع)).scalar() or 0
        districts = db.session.query(Member.حي).distinct().count()
        
        stats = {
            'total_members': total_members,
            'total_amount': float(total_amount),
            'districts': districts,
            'average_amount': float(total_amount / total_members) if total_members > 0 else 0
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
    try:
        # Test database connection
        member_count = Member.query.count()
        return jsonify({
            'status': 'healthy',
            'message': 'الخادم وقاعدة البيانات يعملان بشكل طبيعي',
            'database': 'connected',
            'total_members': member_count
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': 'خطأ في الاتصال بقاعدة البيانات',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Print startup information
    print("=" * 60)
    print("🚀 Flask API Server - نظام إدارة الشقق السكنية")
    print("🗄️ قاعدة بيانات: PostgreSQL")
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
        debug=False,
        host='0.0.0.0',
        port=port
    )