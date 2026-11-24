"""Cost model for "The 32 TB Crossover".

Reproduces every cost table in the paper from a handful of input prices.
Change the numbers in PRICES to your own local prices and run:

    python model/crossover.py

All prices are in Korean won (KRW) and were observed on 2026-11-24.
"""

PRICES = {
    # Blu-ray media: 50 GB BD-R (dual layer), 50 discs for about 80,000 KRW
    "disc_price": 80_000 / 50,          # KRW per disc
    "disc_gb": 50,                      # GB per disc
    # Hard disk: Seagate SkyHawk AI 32 TB, lowest Naver Shopping price
    "hdd_price": 2_428_000,
    "hdd_tb": 32,
    # SSD: Samsung 9100 PRO 8 TB NVMe, lowest Naver Shopping price
    "ssd_price": 3_975_000,
    "ssd_tb": 8,
    # SSD front tier for the appliance: Samsung 870 EVO 1 TB
    "cache_ssd": 386_442,
}

# Fixed appliance hardware (everything except the SSD front tier and the discs)
SCENARIOS = {
    "S1 author estimate (hardware 1,000,000 KRW)": 1_000_000,
    "S2 robot-free 20-drive build (20 x 50,000 + 250,000)": 20 * 50_000 + 250_000,
}

CAPACITIES_TB = [1, 10, 32, 100, 500, 1000]
GB_PER_TB = 1000


def per_gb(price, tb):
    return price / (tb * GB_PER_TB)


def blu_ray_total(fixed_hw, tb, fill=1.0):
    p = PRICES
    discs = tb * GB_PER_TB / (p["disc_gb"] * fill)
    return fixed_hw + p["cache_ssd"] + discs * p["disc_price"], discs


def crossover_tb(fixed_hw, fill=1.0, hdd_gb=None):
    p = PRICES
    fixed = fixed_hw + p["cache_ssd"]
    bd_gb = p["disc_price"] / (p["disc_gb"] * fill)
    hdd_gb = hdd_gb if hdd_gb is not None else per_gb(p["hdd_price"], p["hdd_tb"])
    return fixed / (hdd_gb - bd_gb) / GB_PER_TB


def won(x):
    return f"{x / 10_000:,.1f}"  # in units of 10,000 KRW (man-won)


def main():
    p = PRICES
    bd = p["disc_price"] / p["disc_gb"]
    hdd = per_gb(p["hdd_price"], p["hdd_tb"])
    ssd = per_gb(p["ssd_price"], p["ssd_tb"])
    print(f"Per GB: Blu-ray {bd:.1f} KRW, HDD {hdd:.1f} KRW, SSD {ssd:.1f} KRW")
    print()
    for name, hw in SCENARIOS.items():
        print(f"== {name}: fixed cost {won(hw + p['cache_ssd'])} man-won (incl. 1 TB SSD tier)")
        print(f"{'TB':>6} {'discs':>8} {'Blu-ray':>12} {'HDD':>12} {'SSD':>12}")
        for tb in CAPACITIES_TB:
            total, discs = blu_ray_total(hw, tb)
            hdd_total = p["hdd_price"] * tb / p["hdd_tb"]
            ssd_total = p["ssd_price"] * tb / p["ssd_tb"]
            print(f"{tb:>6} {discs:>8,.0f} {won(total):>12} {won(hdd_total):>12} {won(ssd_total):>12}")
        print(f"Crossover vs HDD (full discs):        {crossover_tb(hw):.1f} TB")
        print(f"Crossover vs HDD (discs 74% full):    {crossover_tb(hw, fill=37.1/50):.1f} TB")
        print(f"Crossover vs HDD at 90 KRW/GB:        {crossover_tb(hw, hdd_gb=90):.1f} TB")
        print()

    # Energy model
    drive_w = 6.3            # W, measured slim Blu-ray writer (OWC)
    write_mb_s = 27          # 6x
    disc_gb = p["disc_gb"]
    hours_per_disc = disc_gb * 1000 / write_mb_s / 3600
    wh_per_tb = drive_w * hours_per_disc * (1000 / disc_gb)
    print(f"Hours per 50 GB disc at 6x (theoretical): {hours_per_disc:.2f} h")
    print(f"Write energy: {wh_per_tb:.0f} Wh per TB written (drive only)")
    print(f"20 drives writing at once: {20 * drive_w:.0f} W, 5 V {20 * drive_w / 5:.1f} A")
    print(f"32 TB (640 discs) with 1 drive: {640 * hours_per_disc:.0f} h, with 20 drives: {640 * hours_per_disc / 20:.1f} h (theoretical)")


if __name__ == "__main__":
    main()
