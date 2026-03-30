import os
import re
import anitopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SubtitleMatcher:
    """字幕匹配器 - 使用anitopy解析动画文件名"""
    
    SUBTITLE_EXTENSIONS = {'.ass', '.srt', '.ssa', '.vtt', '.sub'}
    VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.m4v', '.flv', '.wmv'}
    
    def __init__(self, bangumi_path: str):
        self.bangumi_path = Path(bangumi_path)
    
    def scan_series(self) -> List[Dict]:
        """扫描所有剧集和季度"""
        series_list = []
        
        if not self.bangumi_path.exists():
            return series_list
        
        for series_dir in self.bangumi_path.iterdir():
            if not series_dir.is_dir():
                continue
            
            series_info = {
                'name': series_dir.name,
                'seasons': []
            }
            
            # 扫描季度
            for season_dir in series_dir.iterdir():
                if not season_dir.is_dir():
                    continue
                
                # 检查是否有视频文件
                video_files = [
                    f for f in season_dir.iterdir() 
                    if f.is_file() and f.suffix.lower() in self.VIDEO_EXTENSIONS
                ]
                
                if video_files:
                    # 提取季度编号
                    season_match = re.search(r'season\s*(\d+)', season_dir.name, re.IGNORECASE)
                    season_num = int(season_match.group(1)) if season_match else 1
                    
                    series_info['seasons'].append({
                        'name': season_dir.name,
                        'number': season_num,
                        'path': str(season_dir),
                        'episode_count': len(video_files)
                    })
            
            if series_info['seasons']:
                # 按季度编号排序
                series_info['seasons'].sort(key=lambda x: x['number'])
                series_list.append(series_info)
        
        return sorted(series_list, key=lambda x: x['name'])
    
    def parse_subtitle_filename(self, filename: str) -> Optional[Dict]:
        """使用anitopy解析字幕文件名"""
        try:
            parsed = anitopy.parse(filename)
            
            # 尝试获取集数
            episode = None
            if 'episode_number' in parsed:
                episode = parsed['episode_number']
                # 如果是字符串列表，取第一个
                if isinstance(episode, list):
                    episode = episode[0]
                episode = str(episode).zfill(2)  # 补零到两位
            
            result = {
                'episode': episode,
                'anime_title': parsed.get('anime_title', ''),
                'release_group': parsed.get('release_group', ''),
                'video_resolution': parsed.get('video_resolution', ''),
                'raw_parsed': parsed
            }
            
            return result if episode else None
            
        except Exception as e:
            print(f"解析文件名失败: {filename}, 错误: {e}")
            return None
    
    def get_video_files(self, season_path: str) -> List[Dict]:
        """获取指定季度的所有视频文件"""
        season_dir = Path(season_path)
        if not season_dir.exists():
            return []
        
        video_files = []
        for video_file in season_dir.iterdir():
            if not video_file.is_file() or video_file.suffix.lower() not in self.VIDEO_EXTENSIONS:
                continue
            
            # 解析视频文件名获取集数
            parsed = anitopy.parse(video_file.name)
            episode = None
            
            if 'episode_number' in parsed:
                episode = parsed['episode_number']
                if isinstance(episode, list):
                    episode = episode[0]
                episode = str(episode).zfill(2)
            
            video_files.append({
                'filename': video_file.name,
                'stem': video_file.stem,  # 不含扩展名的文件名
                'path': str(video_file),
                'episode': episode
            })
        
        # 按集数排序
        video_files.sort(key=lambda x: x['episode'] if x['episode'] else '')
        return video_files
    
    def match_subtitle(self, subtitle_path: str, season_path: str, episode: str) -> Tuple[bool, str]:
        """
        将字幕文件匹配到指定季度的指定集数
        
        Args:
            subtitle_path: 字幕文件路径
            season_path: 季度目录路径
            episode: 集数（如 '01', '02'）
        
        Returns:
            (成功标志, 消息)
        """
        subtitle_file = Path(subtitle_path)
        season_dir = Path(season_path)
        
        if not subtitle_file.exists():
            return False, "字幕文件不存在"
        
        if not season_dir.exists():
            return False, "季度目录不存在"
        
        # 获取视频文件列表
        video_files = self.get_video_files(season_path)
        
        # 查找匹配的视频文件
        target_video = None
        for video in video_files:
            if video['episode'] == episode:
                target_video = video
                break
        
        if not target_video:
            return False, f"未找到第 {episode} 集的视频文件"
        
        # 构造新的字幕文件名（使用视频文件的stem + 字幕扩展名）
        new_subtitle_name = target_video['stem'] + subtitle_file.suffix
        new_subtitle_path = season_dir / new_subtitle_name
        
        # 检查目标文件是否已存在
        if new_subtitle_path.exists():
            return False, f"字幕文件已存在: {new_subtitle_name}"
        
        # 复制字幕文件到目标位置
        try:
            import shutil
            shutil.copy2(subtitle_file, new_subtitle_path)
            return True, f"字幕已成功匹配到: {new_subtitle_name}"
        except Exception as e:
            return False, f"复制文件失败: {str(e)}"
