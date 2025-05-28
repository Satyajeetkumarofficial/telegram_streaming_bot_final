import os
import subprocess

def convert_to_hls(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    command = [
        'ffmpeg', '-i', input_path,
        '-filter_complex',
        "[0:v]split=6[v1][v2][v3][v4][v5][v6];"
        "[v1]scale=w=1920:h=1080[v1out];"
        "[v2]scale=w=1280:h=720[v2out];"
        "[v3]scale=w=854:h=480[v3out];"
        "[v4]scale=w=640:h=360[v4out];"
        "[v5]scale=w=426:h=240[v5out];"
        "[v6]scale=w=256:h=144[v6out]",
        '-map', '[v1out]', '-c:v:0', 'libx264', '-b:v:0', '5000k',
        '-map', '[v2out]', '-c:v:1', 'libx264', '-b:v:1', '3000k',
        '-map', '[v3out]', '-c:v:2', 'libx264', '-b:v:2', '1500k',
        '-map', '[v4out]', '-c:v:3', 'libx264', '-b:v:3', '800k',
        '-map', '[v5out]', '-c:v:4', 'libx264', '-b:v:4', '400k',
        '-map', '[v6out]', '-c:v:5', 'libx264', '-b:v:5', '200k',
        '-f', 'hls', '-hls_time', '4', '-hls_playlist_type', 'vod',
        '-master_pl_name', 'master.m3u8',
        '-var_stream_map', 'v:0 v:1 v:2 v:3 v:4 v:5',
        os.path.join(output_dir, 'stream_%v.m3u8')
    ]
    subprocess.run(command)
