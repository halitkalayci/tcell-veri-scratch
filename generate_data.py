#!/usr/bin/env python3
"""
Kirli sentetik telekom verisi üreteci (stdlib only, seed=42).

Kullanım — repo kökünde durarak, repo DIŞINDAKİ bu dosyayı çalıştır:
  python ..\generate_data.py --quick --out data     # 10k abone, 300k CDR (~20 sn)
  python ..\generate_data.py --out data             # 50k abone, 2M CDR (~2-3 dk)
CSV'ler --out klasörüne, ANSWER_KEY.md bu dosyanın yanına (repo dışına) yazılır.
Bu dosya ve ANSWER_KEY repoda durmaz: Copilot workspace'i tarar, demo bozulur.

Kirlilik BİLEREK:
  - msisdn formatı karışık: +905..., 05..., 905..., 5...
  - subscribers: ~%1.5 msisdn iki kez (eski CHURNED + yeni ACTIVE kayıt) -> fan-out tuzağı
  - status varyantları: ACTIVE/active/Aktif/SUSPENDED/CHURNED/churned
  - cdr_events: ~%2 duplicate event_id (farklı ingested_at)
  - ingested_at gecikmesi: %90 <1s, %8 1-24s, %2 24-72s -> late-arriving tuzağı
  - event_type casing varyantları + %0.3 'mms' (geçersiz)
"""
import argparse, csv, os, random, hashlib
from datetime import datetime, timedelta, date
from collections import defaultdict

random.seed(42)
HERE = os.path.dirname(os.path.abspath(__file__))

CITIES = ["Istanbul","Ankara","Izmir","Bursa","Antalya","Adana","Konya","Gaziantep","Kocaeli","Mersin",
          "Kayseri","Eskisehir","Diyarbakir","Samsun","Denizli","Sakarya","Trabzon","Erzurum","Van","Malatya"]
CITY_W = [30,12,9,6,6,4,3,3,3,3,2,2,2,2,2,2,2,2,2,2]
SEGMENTS = ["YOUTH","MASS","PREMIUM","CORPORATE"]
SEG_W    = [20,55,15,10]
PLANS = [("P01","Genç 10GB","YOUTH",149.0),("P02","Genç 20GB","YOUTH",199.0),
         ("P03","Süper 15GB","MASS",229.0),("P04","Süper 30GB","MASS",299.0),
         ("P05","Platinum 50GB","PREMIUM",449.0),("P06","Platinum Sınırsız","PREMIUM",699.0),
         ("P07","Kurumsal Standart","CORPORATE",349.0),("P08","Kurumsal Plus","CORPORATE",599.0)]
PLAN_BY_SEG = {s:[p[0] for p in PLANS if p[2]==s] for s in SEGMENTS}
CHANNELS = ["APP","WEB","DEALER","BANK","IVR"]; CH_W=[45,15,25,10,5]
COUNTRIES = ["TR"]*97 + ["DE","NL","GB"]
STATUS_VARIANTS = {"ACTIVE":["ACTIVE","ACTIVE","ACTIVE","active","Aktif"],
                   "SUSPENDED":["SUSPENDED","suspended"],
                   "CHURNED":["CHURNED","churned"]}
ETYPE_VARIANTS = {"voice":["voice","voice","voice","VOICE","Voice"],
                  "sms":["sms","sms","sms","SMS"],
                  "data":["data","data","data","DATA","Data"]}

DATA_START = datetime(2026,6,1)
DATA_END   = datetime(2026,9,5)
AUG_START, AUG_END = datetime(2026,8,1), datetime(2026,9,1)

def canon(n):  # +905XXXXXXXXX
    return "+90" + n
def dirty_msisdn(n):
    r = random.random()
    if r < 0.60: return "+90"+n
    if r < 0.85: return "0"+n
    if r < 0.95: return "90"+n
    return n
def rand_ts(a, b):
    return a + timedelta(seconds=random.randint(0, int((b-a).total_seconds())))
def iso(dt): return dt.strftime("%Y-%m-%d %H:%M:%S")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "data"), help="CSV çıktı klasörü (repo/data)")
    a = ap.parse_args()
    OUT = os.path.abspath(a.out); os.makedirs(OUT, exist_ok=True)
    n_subs = 10_000 if a.quick else 50_000
    n_cdr  = 300_000 if a.quick else 2_000_000
    n_rech = 60_000 if a.quick else 300_000
    print(f"Üretiliyor: {n_subs} abone, {n_cdr} CDR, {n_rech} yükleme ...")

    # ---------- subscribers ----------
    subs = {}
    rows_sub = []
    sid = 100000
    numbers = set()
    while len(numbers) < n_subs:
        numbers.add("5" + str(random.randint(300000000, 559999999)))
    numbers = sorted(numbers)
    dup_msisdns = set(random.sample(numbers, int(n_subs*0.015)))   # fan-out tuzağı
    for n in numbers:
        seg = random.choices(SEGMENTS, SEG_W)[0]
        city = random.choices(CITIES, CITY_W)[0]
        st = random.choices(["ACTIVE","SUSPENDED","CHURNED"], [82,6,12])[0]
        act = date(2026,1,1) - timedelta(days=random.randint(0, 2000))
        plan = random.choice(PLAN_BY_SEG[seg])
        if n in dup_msisdns:
            # eski kayıt: churned, eski tarih
            sid += 1
            rows_sub.append([sid, dirty_msisdn(n) if random.random()<0.3 else canon(n), random.choice(PLAN_BY_SEG[seg]),
                             random.choice(STATUS_VARIANTS["CHURNED"]), act - timedelta(days=random.randint(400,1500)), city, seg])
            st = "ACTIVE"
        sid += 1
        rows_sub.append([sid, dirty_msisdn(n) if random.random()<0.10 else canon(n), plan,
                         random.choice(STATUS_VARIANTS[st]), act, city, seg])
        subs[n] = {"status":st, "segment":seg, "plan":plan, "city":city, "act":act}
    random.shuffle(rows_sub)
    with open(os.path.join(OUT, "raw_subscribers.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["subscriber_id","msisdn","plan_id","status","activation_date","city","segment"])
        for r in rows_sub: w.writerow(r)

    # kurumsal hatlar: skew için ~40 numara çok yoğun
    heavy = random.sample([n for n in numbers if subs[n]["segment"]=="CORPORATE"], 40)

    # ---------- cdr_events ----------
    aug_active = set()
    dup_count = 0; late24 = 0; invalid_type = 0
    rows_written = 0
    weights = [1]*len(numbers)
    heavy_idx = {numbers.index(h) for h in heavy}
    for i in heavy_idx: weights[i] = 60
    with open(os.path.join(OUT, "raw_cdr_events.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["event_id","msisdn","event_type","event_ts","duration_sec","bytes","cell_id","country_code","ingested_at"])
        chosen = random.choices(numbers, weights, k=n_cdr)
        for k, n in enumerate(chosen):
            et_base = random.choices(["voice","sms","data"],[35,15,50])[0]
            ts = rand_ts(DATA_START, DATA_END)
            r = random.random()
            if r < 0.90: delay = timedelta(seconds=random.randint(1,3600))
            elif r < 0.98: delay = timedelta(seconds=random.randint(3600, 86400))
            else: delay = timedelta(seconds=random.randint(86400, 259200))
            if delay.total_seconds() > 86400: late24 += 1
            ing = ts + delay
            if random.random() < 0.003:
                et = "mms"; invalid_type += 1
            else:
                et = random.choice(ETYPE_VARIANTS[et_base])
            dur = random.randint(5, 1800) if et_base=="voice" else 0
            byt = random.randint(10_000, 500_000_000) if et_base=="data" else 0
            cell = f"{subs[n]['city'][:3].upper()}-{random.randint(1000,9999)}"
            cc = random.choice(COUNTRIES)
            eid = hashlib.md5(f"{k}-{n}".encode()).hexdigest()[:16]
            w.writerow([eid, dirty_msisdn(n), et, iso(ts), dur, byt, cell, cc, iso(ing)]); rows_written += 1
            if AUG_START <= ts < AUG_END and et != "mms":   # tanım: voice/sms/data
                aug_active.add(n)
            if random.random() < 0.02:   # duplicate
                w.writerow([eid, dirty_msisdn(n), et, iso(ts), dur, byt, cell, cc, iso(ing + timedelta(seconds=random.randint(60,7200)))])
                rows_written += 1; dup_count += 1

    # ---------- recharges ----------
    true_by_ch = defaultdict(float); naive_fanout_by_ch = defaultdict(float)
    sub_rows_per_canon = defaultdict(int); raw_sub_strings = set()
    for r in rows_sub:
        n10 = r[1][-10:]; sub_rows_per_canon[n10] += 1; raw_sub_strings.add(r[1])
    lost_on_raw_join = 0
    with open(os.path.join(OUT, "raw_recharges.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["recharge_id","msisdn","amount_try","channel","recharge_ts"])
        for k in range(n_rech):
            n = random.choice(numbers)
            amt = random.choice([50,75,100,150,200,250,300,500]) + (random.choice([0,0,0.5,0.99]))
            ch = random.choices(CHANNELS, CH_W)[0]
            ts = rand_ts(DATA_START, DATA_END)
            m = dirty_msisdn(n)
            w.writerow([200000+k, m, f"{amt:.2f}", ch, iso(ts)])
            true_by_ch[ch] += amt
            naive_fanout_by_ch[ch] += amt * sub_rows_per_canon[n]
            if m not in raw_sub_strings: lost_on_raw_join += 1

    # ---------- plans / campaigns / responses / plan_changes / corporate ----------
    with open(os.path.join(OUT, "raw_plans.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["plan_id","plan_name","plan_family","monthly_fee"])
        for p in PLANS: w.writerow(p)
    camps=[]
    with open(os.path.join(OUT, "raw_campaigns.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["campaign_id","name","start_date","end_date","target_segment"])
        for i in range(40):
            s = date(2026,6,1)+timedelta(days=random.randint(0,80)); e = s+timedelta(days=random.randint(7,30))
            seg = random.choice(SEGMENTS); cid=f"CMP-{i+1:03d}"
            camps.append((cid,seg)); w.writerow([cid, f"{seg.title()} Kampanya {i+1}", s, e, seg])
    with open(os.path.join(OUT, "raw_campaign_responses.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["response_id","campaign_id","msisdn","responded_at","accepted"])
        for k in range(n_subs//2):
            cid,seg = random.choice(camps); n=random.choice(numbers)
            w.writerow([300000+k, cid, dirty_msisdn(n), iso(rand_ts(DATA_START,DATA_END)), random.random()<0.35])
    n_changes = 0
    with open(os.path.join(OUT, "raw_plan_changes.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["msisdn","old_plan_id","new_plan_id","changed_at"])
        for n in random.sample(numbers, n_subs//10):
            seg=subs[n]["segment"]; old=subs[n]["plan"]; new=random.choice([p for p in PLAN_BY_SEG[seg] if p!=old] or [old])
            w.writerow([canon(n), old, new, iso(rand_ts(datetime(2026,7,1), DATA_END))]); n_changes+=1
    with open(os.path.join(OUT, "raw_corporate_accounts.csv"), "w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["account_id","parent_account_id","account_name","msisdn"])
        w.writerow(["ACC-1","","Holding A",""])
        w.writerow(["ACC-1-1","ACC-1","A Lojistik",""]); w.writerow(["ACC-1-2","ACC-1","A Enerji",""])
        w.writerow(["ACC-1-1-1","ACC-1-1","A Lojistik Marmara",""]); w.writerow(["ACC-1-1-2","ACC-1-1","A Lojistik Ege",""])
        for i,h in enumerate(heavy[:12]):
            parent = ["ACC-1-1-1","ACC-1-1-2","ACC-1-2"][i%3]
            w.writerow([f"LINE-{i+1}", parent, f"Hat {i+1}", canon(h)])

    # ---------- answer key (repo DIŞINA) ----------
    active_by_seg = defaultdict(int)
    for n in aug_active:
        if subs[n]["status"]=="ACTIVE": active_by_seg[subs[n]["segment"]] += 1
    naive_status_active_rows = sum(1 for r in rows_sub if r[3]=="ACTIVE")
    with open(os.path.join(HERE,"ANSWER_KEY.md"), "w", encoding="utf-8") as f:
        f.write("# ANSWER KEY — eğitmen kopyası, repoya girmez\n\n")
        f.write(f"Üretim: {'quick' if a.quick else 'full'} | seed=42\n\n")
        f.write("## Veri kirliliği\n")
        f.write(f"- raw.cdr_events satır: {rows_written} | tekil event_id: {rows_written-dup_count} | duplicate satır: {dup_count}\n")
        f.write(f"- late-arriving (ingested_at - event_ts > 24 saat): {late24}\n")
        f.write(f"- geçersiz event_type ('mms'): {invalid_type}\n")
        f.write(f"- raw.subscribers satır: {len(rows_sub)} | tekil msisdn: {n_subs} | iki kaydı olan msisdn: {len(dup_msisdns)}\n")
        f.write(f"- status tam olarak 'ACTIVE' yazan satır: {naive_status_active_rows} (varyantlar dahil değil!)\n\n")
        f.write("## Ağustos 2026 aktif abone (>=1 geçerli CDR ve güncel kaydın statüsü ACTIVE)\n")
        for s in SEGMENTS: f.write(f"- {s}: {active_by_seg[s]}\n")
        f.write(f"- TOPLAM: {sum(active_by_seg.values())}\n")
        f.write(f"- (Sadece 'Ağustos'ta CDR üreten' tekil msisdn, statü bakılmadan: {len(aug_active)})\n\n")
        f.write("## Kanal bazında toplam yükleme (TRY), tüm dönem\n")
        f.write("| channel | DOĞRU toplam | fan-out'lu (subscribers'a naif join) |\n|---|---|---|\n")
        for ch in CHANNELS: f.write(f"| {ch} | {true_by_ch[ch]:.2f} | {naive_fanout_by_ch[ch]:.2f} |\n")
        f.write(f"\n- msisdn normalize ETMEDEN subscribers'a inner join yapılırsa kaybolan yükleme satırı: {lost_on_raw_join}\n")
        f.write(f"\n## plan_changes satır: {n_changes}\n")
    print("Bitti. CSV'ler:", OUT)
    print("Cevap anahtarı:", os.path.join(HERE, "ANSWER_KEY.md"), "(repo dışında — Copilot okumasın)")

if __name__ == "__main__":
    main()