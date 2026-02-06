import time

print("Starting import timing test...")
start_time = time.time()

t0 = time.time()
import streamlit as st
print(f"Streamlit import: {time.time() - t0:.2f}s")

t0 = time.time()
import pandas as pd
print(f"Pandas import: {time.time() - t0:.2f}s")

t0 = time.time()
import soundfile as sf
print(f"Soundfile import: {time.time() - t0:.2f}s")

t0 = time.time()
import config
print(f"Config import: {time.time() - t0:.2f}s")

# Test metrics imports if they were to happen (simulating potential leakage)
t0 = time.time()
try:
    import metrics.srmr_metric
    print(f"SRMR metric import: {time.time() - t0:.2f}s")
except Exception as e:
    print(f"SRMR import failed: {e}")

total_time = time.time() - start_time
print(f"Total startup time: {total_time:.2f}s")
