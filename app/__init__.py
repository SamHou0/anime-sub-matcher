import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from .subtitle_matcher import SubtitleMatcher

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'
BANGUMI_FOLDER = Path(__file__).parent.parent / 'bangumi'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
UPLOAD_FOLDER.mkdir(exist_ok=True)

# 初始化字幕匹配器
matcher = SubtitleMatcher(str(BANGUMI_FOLDER))


@app.route('/')
def index():
    """返回主页"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/series', methods=['GET'])
def get_series():
    """获取所有剧集和季度信息"""
    try:
        series_list = matcher.scan_series()
        return jsonify({
            'success': True,
            'data': series_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_subtitle():
    """
    上传字幕文件并解析集数
    返回: {success: bool, data: {filename, episode, parsed_info}, error: str}
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': '没有上传文件'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': '文件名为空'
        }), 400
    
    # 检查文件扩展名
    original_filename = file.filename
    file_ext = Path(original_filename).suffix.lower()
    
    if file_ext not in matcher.SUBTITLE_EXTENSIONS:
        return jsonify({
            'success': False,
            'error': f'不支持的文件类型: {file_ext}。支持的格式: {", ".join(matcher.SUBTITLE_EXTENSIONS)}'
        }), 400
    
    try:
        # 先解析原始文件名获取集数
        parsed = matcher.parse_subtitle_filename(original_filename)
        
        if not parsed or not parsed['episode']:
            return jsonify({
                'success': False,
                'error': '无法从文件名中识别集数。请确保文件名包含集数信息（如 [01], E01, EP01 等）',
                'filename': original_filename
            }), 400
        
        # 生成安全的文件名用于保存 (使用原始文件名而不是secure_filename)
        # 使用时间戳避免文件名冲突
        import time
        safe_filename = f"{int(time.time())}_{original_filename}"
        filepath = UPLOAD_FOLDER / safe_filename
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'data': {
                'filename': original_filename,
                'filepath': str(filepath),
                'episode': parsed['episode'],
                'anime_title': parsed['anime_title'],
                'release_group': parsed['release_group'],
                'parsed_info': parsed['raw_parsed']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }), 500


@app.route('/api/season/episodes', methods=['GET'])
def get_season_episodes():
    """
    获取指定季度的所有剧集信息
    参数: season_path
    """
    season_path = request.args.get('season_path', '')
    
    if not season_path:
        return jsonify({
            'success': False,
            'error': '缺少 season_path 参数'
        }), 400
    
    try:
        episodes = matcher.get_video_files(season_path)
        return jsonify({
            'success': True,
            'data': episodes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/match', methods=['POST'])
def match_subtitle():
    """
    匹配字幕到指定季度的指定集数
    POST JSON: {subtitle_path, season_path, episode}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': '请求数据为空'
        }), 400
    
    subtitle_path = data.get('subtitle_path', '')
    season_path = data.get('season_path', '')
    episode = data.get('episode', '')
    
    if not all([subtitle_path, season_path, episode]):
        return jsonify({
            'success': False,
            'error': '缺少必要参数: subtitle_path, season_path, episode'
        }), 400
    
    try:
        success, message = matcher.match_subtitle(subtitle_path, season_path, episode)
        
        # 如果成功，删除上传的临时文件
        if success:
            try:
                Path(subtitle_path).unlink()
            except:
                pass  # 忽略删除失败
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'匹配失败: {str(e)}'
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'error': f'文件过大。最大允许大小: {MAX_FILE_SIZE / 1024 / 1024:.0f}MB'
    }), 413


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
