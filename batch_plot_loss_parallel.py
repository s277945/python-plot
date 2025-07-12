import os
import glob
import subprocess
from concurrent.futures import ThreadPoolExecutor

LOGDIR = "logs_test"
OUTDIR = "output_plots"
SCRIPT = "plotMoqjsTimestamp.py"
THREADS = 16  # Modifica qui il grado di parallelismo

os.makedirs(OUTDIR, exist_ok=True)
logfiles = glob.glob(os.path.join(LOGDIR, "*.txt"))

def worker(logfile):
    basename = os.path.basename(logfile)
    outname = os.path.splitext(basename)[0] + "_cumuloss.png"
    print(f"Plotting {basename} ...")
    subprocess.run([
        "h:/Tesi/python-plot/Scripts/python.exe", SCRIPT,
        "-sks", "150",
        "-mh", "auto",
        "-shl", "true",
        "-f", logfile,
        "-sf", "true",
        "-lsth", "last5_mean"
    ])
    # Sposta il file se prodotto in cwd
    if os.path.exists(outname):
        os.replace(outname, os.path.join(OUTDIR, outname))

with ThreadPoolExecutor(max_workers=THREADS) as pool:
    pool.map(worker, logfiles)

print(f"\nFatto! Trovi tutti i plot in {OUTDIR}")