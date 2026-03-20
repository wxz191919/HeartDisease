from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_cors import CORS
from models.user import db, User  # 确保导入User模型
from routes.auth import auth_bp
from routes.data import data_bp
from routes.patients import patients_bp
from routes.predictions import predictions_bp
from config import Config
import logging
from datetime import timedelta

# === 🚀 只新增：导入读取文件所需的模块 ===
import os
import pandas as pd


def create_app():
    # 配置日志
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    app.config.from_object(Config)

    # --- 添加日志：检查 SECRET_KEY ---
    logger.debug(f"Loaded SECRET_KEY: {app.config.get('SECRET_KEY')}")
    # --- 结束日志 ---

    # JWT配置
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY  # 从配置获取
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)

    # 配置用户加载器
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
		指定JWT的identity是用户ID
		参数user可能是：
		- User对象（登录时）
		- 用户ID整数（验证token时）
		"""
        if isinstance(user, int):  # 如果是整数直接返回
            return user
        return user.id  # 如果是用户对象返回其id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """从JWT中获取用户对象"""
        from models.user import User  # 避免循环导入
        user_id = jwt_data["sub"]
        return User.query.get(user_id)

    # 可选：添加自定义声明
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        """向JWT添加自定义声明（如用户角色）"""
        user = User.query.get(identity)
        return {
            'role': user.role,
            'username': user.username
        }

    # CORS配置 (恢复之前的配置)
    app.config['CORS_HEADERS'] = 'Content-Type'  # 取消注释
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })
    # CORS(app, supports_credentials=True) # 注释掉简化的配置

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(data_bp, url_prefix='/api')
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')

    logger.info('Registered blueprints:')
    logger.info(f'Auth blueprint: /api/auth')
    logger.info(f'Data blueprint: /api')
    logger.info(f'Patients blueprint: /api/patients')
    logger.info(f'Predictions blueprint: /api/predictions')

    # 创建数据库表
    with app.app_context():
        db.create_all()
        logger.info('Database tables created')

    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'jwt_configured': True})

    # ==========================================================
    # 🚀 只新增：全球真实心脏病数据提炼接口 (用于大屏)
    # ==========================================================
    @app.route('/api/global-analysis', methods=['GET'])
    def get_global_analysis():
        try:
            # 精准指向 backend/uploads 文件夹
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, 'uploads', 'global_cvd_burden_2025_2050.csv')

            if not os.path.exists(data_path):
                return jsonify({'success': False, 'message': f'找不到 CSV 文件，请确认是否已将文件放入: {data_path}'})

            df = pd.read_csv(data_path)

            # 提取 2025 年的截面数据
            df_2025 = df[df['year'] == 2025]

            # 测算各项指标
            total_deaths = int(df_2025['crude_cvd_deaths'].sum())
            continent_group = df_2025.groupby('continent')['crude_cvd_deaths'].sum().reset_index()
            continent_data = [{'name': row['continent'], 'value': int(row['crude_cvd_deaths'])} for _, row in
                              continent_group.iterrows()]

            risk_factors = [
                {'name': '高血压致死', 'value': round(df_2025['high_sbp_attributable_deaths_pct'].mean(), 1)},
                {'name': '高LDL(胆固醇)致死', 'value': round(df_2025['high_ldl_attributable_deaths_pct'].mean(), 1)},
                {'name': '高BMI(肥胖)致死', 'value': round(df_2025['high_bmi_attributable_deaths_pct'].mean(), 1)},
                {'name': '吸烟致死', 'value': round(df_2025['tobacco_attributable_deaths_pct'].mean(), 1)}
            ]

            trend_group = df.groupby('year')['crude_cvd_deaths'].sum().reset_index()
            trend_years = [int(y) for y in trend_group['year']]
            trend_deaths = [int(d) for d in trend_group['crude_cvd_deaths']]

            # 提取国家数据给地图用
            country_data = []
            for _, row in df_2025.iterrows():
                country_data.append({
                    'name': str(row['country']),
                    'value': round(float(row['crude_mortality_rate_per_100k']), 2)
                })

            return jsonify({
                'success': True,
                'data': {
                    'total_deaths': total_deaths,
                    'continent_data': continent_data,
                    'risk_factors': risk_factors,
                    'trend': {
                        'years': trend_years,
                        'deaths': trend_deaths
                    },
                    'country_data': country_data
                }
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    # CORS(app) # <--- 删除这一行，因为已在 create_app 中配置
    app.run(host='127.0.0.1', port=5003, debug=True)