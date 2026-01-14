from pathlib import Path
from moviepy import VideoFileClip
import imageio.v2 as imageio

#config
VIDEO_PATH = Path("input.mp4")
OUTPUT_SS = Path("screenshots")
#change number of screenshots here
N_SHOTS = 100
IMAGE_FORMAT = "png"

def main() -> None:
    if not VIDEO_PATH.exists():
        raise FileNotFoundError(f"Video not found: {VIDEO_PATH.resolve()}")

    OUTPUT_SS.mkdir(parents=True, exist_ok=True)

    with VideoFileClip(str(VIDEO_PATH)) as clip:
        duration = clip.duration #Sseconds
        if duration <= 0:
            raise ValueError("Video duration invalid.")

        # time between ss
        step = duration / N_SHOTS

        # output info
        print(f"Duration: {duration:.2f}s")
        print(f"Saving {N_SHOTS} screenshots to: {OUTPUT_SS.resolve()}")
        print(f"Interval: ~{step:.2f}s")

        for i in range(N_SHOTS):
            t = min(i * step, duration - 0.1)  #out of bounds error prev.
            frame = clip.get_frame(t)  #numpy array

            out_file = OUTPUT_SS / f"shot_{i+1:03d}_{t:07.2f}s.{IMAGE_FORMAT}"
            imageio.imwrite(out_file, frame)

            if (i + 1) % 10 == 0 or (i + 1) == N_SHOTS:
               print(f"Saved {i+1}/{N_SHOTS}: {out_file.name}")

    print("Done.")

if __name__ == "__main__":
    main()