#!/usr/bin/env python
# coding: utf-8

# In[1]:


# save_as: lifepharmacy_self_medications_to_csv.py
import requests, csv, time, re, html

BASE = "https://prodapp.lifepharmacy.com/api/web/products"
PARAMS = {
    "categories": "self-medications",
    "lang": "ae-en",
    "new_method": "true",
    "take": 100,   # use 20/50 if 100 is rejected or unstable
}
OUTFILE = "lifepharmacy_self_medications.csv"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

def strip_html(s):
    if not s:
        return ""
    # unescape HTML entities first, then remove tags
    s = html.unescape(s)
    return re.sub(r"<[^>]+>", " ", s).replace("\xa0", " ").strip()

def get_list(obj):
    """
    API returns: {"success":true, "data":{"products":[...]}, ...}
    Fallbacks kept in case the wrapper changes.
    """
    if isinstance(obj, dict):
        data = obj.get("data") or {}
        if isinstance(data, dict) and isinstance(data.get("products"), list):
            return data["products"]
        # generic fallbacks
        for k in ("items","products","result","data"):
            v = obj.get(k)
            if isinstance(v, list): return v
            if isinstance(v, dict) and isinstance(v.get("products"), list): return v["products"]
    return []

def flatten(p):
    # top-level
    pid        = p.get("id") or p.get("_id")
    title      = p.get("title") or p.get("name")
    slug       = p.get("slug")
    price      = p.get("price")
    is_taxable = p.get("is_taxable")
    active     = p.get("active")
    sku        = p.get("sku")

    # inventory
    inv        = p.get("inventory") or {}
    inv_sku    = inv.get("sku")
    inv_upc    = inv.get("upc")

    # brand
    brand      = p.get("brand") or {}
    brand_id   = brand.get("id") or brand.get("_id")
    brand_name = brand.get("name")
    brand_slug = brand.get("slug")

    # category (primary) + categories (list)
    cat        = p.get("category") or {}
    cat_name   = cat.get("name")
    cat_slug   = cat.get("slug")
    cats       = p.get("categories") or []
    cats_names = " > ".join([c.get("name","") for c in cats if isinstance(c, dict) and c.get("name")])

    # text fields
    description        = strip_html(p.get("description"))
    short_description  = strip_html(p.get("short_description"))

    # images
    images     = p.get("images") or {}
    featured   = images.get("featured_image")
    gallery    = images.get("gallery_images") or []
    gallery_1  = gallery[0].get("image") if gallery and isinstance(gallery[0], dict) else ""

    # timestamps
    created_at = p.get("created_at")
    updated_at = p.get("updated_at")

    product_url = f"https://www.lifepharmacy.com/product/{slug}" if slug else ""

    return {
        "id": pid,
        "_id": p.get("_id"),
        "title": title,
        "slug": slug,
        "price_aed": price,
        "is_taxable": is_taxable,
        "active": active,
        "sku": sku,
        "inventory_sku": inv_sku,
        "inventory_upc": inv_upc,
        "brand_id": brand_id,
        "brand_name": brand_name,
        "brand_slug": brand_slug,
        "category_name": cat_name,
        "category_slug": cat_slug,
        "categories_path": cats_names,
        "description_text": description,
        "short_description_text": short_description,
        "image_featured": featured,
        "image_gallery_first": gallery_1,
        "created_at": created_at,
        "updated_at": updated_at,
        "product_url": product_url,
    }



import pandas as pd
import requests
import time

def lifepharmacy():
    session = requests.Session()
    session.headers.update(HEADERS)

    take = int(PARAMS["take"])
    skip = 0
    rows = []
    page = 0

    while True:
        q = dict(PARAMS, skip=skip)
        try:
            r = session.get(BASE, params=q, timeout=30)
            
            if r.status_code == 429:
                time.sleep(2)
                continue
                
            r.raise_for_status()
            data = r.json()

            products = get_list(data)
            if not products:
                break

            rows.extend(flatten(p) for p in products)
            print(f"Page {page}: Scraped {len(products)} products")
            
            page += 1
            skip += take
            time.sleep(0.2)
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    if not rows:
        print("No products found.")
        return pd.DataFrame()

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(rows)
    
    print(f"Total rows scraped: {len(df)}")
    return df


lifepharmacy_df = lifepharmacy()


# In[2]:


# save as: binsina_dl4objects_to_csv.py
import re, json, csv, time
import requests
import pandas as pd
import time

BASE_URL = "https://www.binsina.ae/en/medical-essentials.html"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "text/html"}
OUTFILE = "binsina_medical_essentials.csv"

# regex to capture: var dl4Objects = [ ... ];
DL4_RE = re.compile(r"var\s+dl4Objects\s*=\s*(\[[\s\S]*?\]);", re.IGNORECASE)

def fetch_html(page: int) -> str:
    params = {"_": "1762877748790", "p": page}  # '_' is optional; keeps parity with your URL
    r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.text

def parse_dl4_items(html_text: str):
    """
    Returns list of item dicts from dl4Objects' ecommerce.items
    """
    m = DL4_RE.search(html_text)
    if not m:
        return []
    raw = m.group(1)
    try:
        dl4 = json.loads(raw)
    except json.JSONDecodeError:
        # Sometimes JS allows trailing commas or unescaped stuff; try a lenient fix if needed
        return []

    items = []
    for obj in dl4:
        ec = obj.get("ecommerce")
        if isinstance(ec, dict) and isinstance(ec.get("items"), list):
            items.extend(ec["items"])
    return items

def pick_fields(item: dict, page: int):
    # Map only what exists in dl4Objects.items (as per your snippet)
    return {
        "page": page,
        "item_name": item.get("item_name"),
        "item_id": item.get("item_id"),
        "price": item.get("price"),
        "item_brand": item.get("item_brand"),
        "item_category": item.get("item_category"),
        "item_list_name": item.get("item_list_name"),
        "item_list_id": item.get("item_list_id"),
        "index": item.get("index"),
    }



def binsina():
    rows = []
    page = 1
    
    while True:
        html = fetch_html(page)
        items = parse_dl4_items(html)
        
        if not items:
            print(f"No items found on page {page}. Stopping.")
            break

        page_rows = [pick_fields(it, page) for it in items]
        rows.extend(page_rows)
        print(f"Page {page}: {len(page_rows)} items")
        
        page += 1
        time.sleep(0.3)  # polite delay

    if not rows:
        print("No items scraped.")
        return pd.DataFrame()  # Return empty DF to maintain type consistency

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(rows)
    
    print(f"Successfully scraped {len(df)} rows.")
    return df


binsina_df = binsina()


# ### Concatenation

# In[3]:


binsina_df['name']=binsina_df['item_name']
binsina_df['description']=''
binsina_df['price']=binsina_df['price']
binsina_df=binsina_df[['name','price']]

lifepharmacy_df['name']=lifepharmacy_df['title']
lifepharmacy_df['price']=lifepharmacy_df['price_aed']
lifepharmacy_df['description']=lifepharmacy_df['description_text']
lifepharmacy_df=lifepharmacy_df[['name','price']]
price_df=pd.concat([binsina_df,lifepharmacy_df])
price_df=price_df[price_df['price']!=0]


# ==========================================
# MASTER FILE UPDATE LOGIC
# ==========================================
MASTER_FILE = "medication_master_multilingual_final.csv"

if not price_df.empty:
    try:
        # 1. Load the existing master dataset
        master_df = pd.read_csv(MASTER_FILE)
        print(f"Loaded master file with {len(master_df)} rows.")

        # 2. Create a lookup dictionary from the scraped data
        # Using lowercase keys for robust matching
        price_lookup = price_df.set_index(price_df['name'].str.lower())['price'].to_dict()

        def update_price(row):
            # Check if current row's name exists in our new price list
            name_key = str(row['Name']).lower().strip()
            if name_key in price_lookup:
                return price_lookup[name_key]
            return row['Price'] # Keep old price if no match found

        # 3. Apply the update
        original_prices = master_df['Price'].copy()
        master_df['Price'] = master_df.apply(update_price, axis=1)
        
        # Calculate how many rows actually changed
        changes = (original_prices != master_df['Price']).sum()
        
        # 4. Save the updated master file
        master_df.to_csv(MASTER_FILE, index=False)
        print(f"Successfully updated {changes} price entries in {MASTER_FILE}.")

    except FileNotFoundError:
        print(f"Error: {MASTER_FILE} not found in the root directory.")
    except Exception as e:
        print(f"An error occurred during the master update: {e}")
else:
    print("Scraping failed or returned no data. Master file was not modified.")


