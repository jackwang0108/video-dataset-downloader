# Standard Library
import os
import multiprocessing
from pathlib import Path
from typing import Optional


# Third-Party Library
from pytube import YouTube

# My Library
from utils.exceptions import ProxyError, VideoNotFoundError
from utils.utils import red, green, yellow, parse_csv, get_proxy_handler, download


def main_worker(filename: str, youtube_id: str, resolution: str, fps: int, outdir: Optional[Path | str] = None):
    """
    执行从YouTube下载视频的任务的工作函数

    Args:
        youtube_id (str): YouTube视频ID.
        resolution (str): YouTube视频分辨率.
        fps (int): YouTube视频FPS

    Returns:
        如果下载成功, 返回True, 否则返回False

    Examples:
        >>> main_worker("cZqaa0b34vk", "720p", 30)
        True
    """

    proxy_ok, proxy = get_proxy_handler(test=True)
    if not proxy_ok:
        return False

    max_retry = 3
    success = False
    print(f"Processing: {filename}")
    while max_retry > 0 and not success:
        try:
            success = download(youtube_id=youtube_id, fps=fps,
                               resolution=resolution, proxy_handler=proxy, output_dir=outdir, filename=filename)
            if success:
                print(f"Download {green('Success')}: {filename}")
        except ProxyError as e:
            max_retry -= 1
            success = False
            print(f"Download video {
                filename} {yellow('failed', True)} because of proxy error, will retry later...")
        except VideoNotFoundError as e:
            max_retry = 0
            success = False
            print(f"Download video {
                filename} {red('failed', True)} because of video not found, failed!")
    return success


def main(outdir: Path | str):
    """
    多进程YouTube视频下载程序入口函数

    Examples:
        >>> main()
        [True]
    """

    videos_to_download = parse_csv("./data/tennis/videos.csv")

    async_results = []
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for filename, video_id, resolution, fps in videos_to_download:
        result = pool.apply_async(
            main_worker, (filename, video_id, resolution, fps, outdir))
        async_results.append(result.get())

    # 等待所有任务完成
    pool.close()
    pool.join()

    results = [
        [video_info[0], async_result.get()]
        for video_info, async_result in zip(videos_to_download, async_results)
    ]

    with open("fs_comp_result.txt", mode="w") as f:
        f.writelines(results)


if __name__ == "__main__":
    main("./datasets/tennis")
