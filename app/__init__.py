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
    上传单个或多个字幕文件并解析集数
    返回: {success: bool, data: [{filename, episode, parsed_info}, ...], errors: [...]}
    """
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'error': '没有上传文件'
        }), 400
    
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({
            'success': False,
            'error': '没有有效的文件'
        }), 400
    
    results = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        original_filename = file.filename
        file_ext = Path(original_filename).suffix.lower()
        
        # 检查文件扩展名
        if file_ext not in matcher.SUBTITLE_EXTENSIONS:
            errors.append({
                'filename': original_filename,
                'error': f'不支持的文件类型: {file_ext}'
            })
            continue
        
        try:
            # 解析原始文件名获取集数
            parsed = matcher.parse_subtitle_filename(original_filename)
            
            if not parsed or not parsed['episode']:
                errors.append({
                    'filename': original_filename,
                    'error': '无法识别集数'
                })
                continue
            
            # 生成安全的文件名用于保存
            import time
            safe_filename = f"{int(time.time() * 1000000)}_{original_filename}"  # 使用微秒避免冲突
            filepath = UPLOAD_FOLDER / safe_filename
            file.save(str(filepath))
            
            results.append({
                'filename': original_filename,
                'filepath': str(filepath),
                'episode': parsed['episode'],
                'anime_title': parsed['anime_title'],
                'release_group': parsed['release_group'],
                'parsed_info': parsed['raw_parsed']
            })
            
        except Exception as e:
            errors.append({
                'filename': original_filename,
                'error': f'处理失败: {str(e)}'
            })
    
    if not results and errors:
        return jsonify({
            'success': False,
            'error': '所有文件处理失败',
            'errors': errors
        }), 400
    
    return jsonify({
        'success': True,
        'data': results,
        'errors': errors if errors else []
    })


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
    POST JSON: {subtitle_path, season_path, episode} 或 {subtitles: [{subtitle_path, episode}], season_path}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': '请求数据为空'
        }), 400
    
    # 支持批量匹配
    if 'subtitles' in data:
        return batch_match_subtitles(data)
    
    # 单个匹配（保持向后兼容）
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
                pass
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'匹配失败: {str(e)}'
        }), 500


def batch_match_subtitles(data):
    """批量匹配字幕"""
    subtitles = data.get('subtitles', [])
    season_path = data.get('season_path', '')
    
    if not subtitles or not season_path:
        return jsonify({
            'success': False,
            'error': '缺少必要参数: subtitles, season_path'
        }), 400
    
    results = []
    success_count = 0
    
    for sub in subtitles:
        subtitle_path = sub.get('subtitle_path', '')
        episode = sub.get('episode', '')
        filename = sub.get('filename', '')
        
        if not subtitle_path or not episode:
            results.append({
                'filename': filename,
                'success': False,
                'message': '缺少必要参数'
            })
            continue
        
        try:
            success, message = matcher.match_subtitle(subtitle_path, season_path, episode)
            
            results.append({
                'filename': filename,
                'episode': episode,
                'success': success,
                'message': message
            })
            
            if success:
                success_count += 1
                # 删除临时文件
                try:
                    Path(subtitle_path).unlink()
                except:
                    pass
                    
        except Exception as e:
            results.append({
                'filename': filename,
                'episode': episode,
                'success': False,
                'message': f'匹配失败: {str(e)}'
            })
    
    return jsonify({
        'success': success_count > 0,
        'total': len(subtitles),
        'success_count': success_count,
        'results': results
    })


@app.errorhandler(413)
def request_entity_too_large(error):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'error': f'文件过大。最大允许大小: {MAX_FILE_SIZE / 1024 / 1024:.0f}MB'
    }), 413


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
