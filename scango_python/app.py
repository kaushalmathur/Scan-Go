import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import io
import qrcode
from PIL import Image
import zxingcpp
import cv2

from database import (
    init_db, SessionLocal, User, Merchant, Outlet, Product, Transaction, CartItem, Scan,
    hash_password, verify_password
)
from ml_engine import ml_pipeline

# --- Page Configuration ---
st.set_page_config(
    page_title="Scan & Go — Queue-Free Retail Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Executive Custom CSS Styling ---
st.markdown("""
<style>
    /* Global Background Gradient */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0f172a 0%, #090d16 100%);
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* App Header Banner */
    .app-header {
        background: linear-gradient(135deg, rgba(2, 128, 144, 0.3) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(0, 245, 212, 0.25);
        border-radius: 1.5rem;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(16px);
    }

    /* Auth Feature Cards */
    .auth-feature-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1.25rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Outlet Card */
    .outlet-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1.25rem;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .outlet-card:hover {
        border-color: rgba(0, 245, 212, 0.4);
        transform: translateY(-2px);
    }

    /* Product Card */
    .product-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.25rem;
        padding: 1.25rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Badges */
    .badge-in-stock {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 0.6rem;
        font-size: 0.75rem;
        font-weight: 800;
    }
    .badge-out-stock {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 0.6rem;
        font-size: 0.75rem;
        font-weight: 800;
    }
    .badge-offer {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 0.6rem;
        font-size: 0.75rem;
        font-weight: 800;
    }
    .badge-new {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 0.6rem;
        font-size: 0.75rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database Schema & Seed Data
init_db()

def get_db():
    return SessionLocal()

# Session State Setup
if 'user' not in st.session_state:
    st.session_state.user = None
if 'active_outlet_id' not in st.session_state:
    st.session_state.active_outlet_id = 1
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'last_scanned' not in st.session_state:
    st.session_state.last_scanned = None
if 'discount_percent' not in st.session_state:
    st.session_state.discount_percent = 0.0

# Available Navigation Pages
customer_pages = [
    "🔐 Account Sign In & Register",
    "🏬 Discover Physical Outlets",
    "🔍 Pre-Visit Store Catalog",
    "📱 In-Store Scan & Go",
    "🛒 Cart & Checkout",
    "🧾 Purchase & Receipt History"
]

merchant_pages = [
    "🔐 Account Sign In & Register",
    "🏢 Outlets Management",
    "📦 Product & Barcode Catalog",
    "⚡ Stock & Offers Manager",
    "📊 Sales Analytics & AI Engine"
]

if 'customer_page' not in st.session_state:
    st.session_state.customer_page = customer_pages[0]
if 'merchant_page' not in st.session_state:
    st.session_state.merchant_page = merchant_pages[0]

# --- QR & Barcode Image Decoder ---
def decode_qr_or_barcode(image_file) -> str:
    try:
        img = Image.open(image_file)
        results = zxingcpp.read_barcodes(img)
        if results and len(results) > 0:
            return results[0].text.strip()

        img_np = np.array(img.convert('RGB'))
        detector = cv2.QRCodeDetector()
        val, _, _ = detector.detectAndDecode(img_np)
        if val and len(val.strip()) > 0:
            return val.strip()
    except Exception as e:
        print("QR Decode exception:", e)
    return None

def add_to_cart_by_barcode(barcode: str, outlet_id: int):
    db = get_db()
    product = db.query(Product).filter(Product.barcode == barcode, Product.outlet_id == outlet_id).first()
    
    if not product:
        product = db.query(Product).filter(Product.barcode == barcode).first()
        if not product:
            product = Product(
                merchant_id=1,
                outlet_id=outlet_id,
                sku=f"QR-{barcode[-4:] if len(barcode)>=4 else '000'}",
                name=f"Scanned Item (#{barcode[-6:] if len(barcode)>=6 else barcode})",
                price=4.99,
                original_price=4.99,
                stock=100,
                is_in_stock=True,
                category="General Grocery",
                barcode=barcode
            )
            db.add(product)
            db.commit()
            db.refresh(product)

    pid = product.id
    if pid in st.session_state.cart:
        st.session_state.cart[pid]['quantity'] += 1
    else:
        st.session_state.cart[pid] = {
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'barcode': product.barcode,
            'quantity': 1,
            'outlet_id': product.outlet_id
        }
    
    st.session_state.last_scanned = product.name
    db.close()

# --- Sidebar Header & Navigation ---
st.sidebar.markdown("### 🛒 Scan & Go `PRO`")
st.sidebar.caption("Multi-Outlet Physical Discovery & Scan & Go Platform")

app_mode = st.sidebar.selectbox("Select Experience Portal", ["👥 Customer Experience Portal", "🏢 Merchant Management Console"])

if st.session_state.user:
    st.sidebar.success(f"Logged in as: **{st.session_state.user['email']}** ({st.session_state.user['role'].upper()})")
    if st.sidebar.button("🔒 Sign Out", type="secondary"):
        st.session_state.user = None
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.info("Please sign in or use 1-click demo buttons below.")
    c_side1, c_side2 = st.columns(2)
    with c_side1:
        if st.sidebar.button("⚡ Demo Customer"):
            db = get_db()
            u = db.query(User).filter(User.email == "customer@scango.com").first()
            if u:
                st.session_state.user = {"id": u.id, "email": u.email, "role": u.role}
                st.session_state.customer_page = "🏬 Discover Physical Outlets"
                st.rerun()
            db.close()
    with c_side2:
        if st.sidebar.button("⚡ Demo Merchant"):
            db = get_db()
            u = db.query(User).filter(User.email == "test@scango.com").first()
            if u:
                st.session_state.user = {"id": u.id, "email": u.email, "role": u.role}
                st.session_state.merchant_page = "🏢 Outlets Management"
                st.rerun()
            db.close()

st.sidebar.markdown("---")

if app_mode == "👥 Customer Experience Portal":
    current_idx = customer_pages.index(st.session_state.customer_page) if st.session_state.customer_page in customer_pages else 0
    selected_page = st.sidebar.radio("Customer Navigation", customer_pages, index=current_idx)
    st.session_state.customer_page = selected_page
else:
    current_idx = merchant_pages.index(st.session_state.merchant_page) if st.session_state.merchant_page in merchant_pages else 0
    selected_page = st.sidebar.radio("Merchant Navigation", merchant_pages, index=current_idx)
    st.session_state.merchant_page = selected_page

st.sidebar.markdown("---")
st.sidebar.markdown("**Tech Stack (100% Python):**")
st.sidebar.code("Streamlit • OpenCV • ZXing\nSQLAlchemy • Pandas • Scikit-Learn")

# --- Top Header Banner ---
db = get_db()
active_outlet_obj = db.query(Outlet).filter(Outlet.id == st.session_state.active_outlet_id).first()
db.close()

outlet_display = active_outlet_obj.name if active_outlet_obj else "Downtown Superstore Outlet #01"
cart_count = sum(i['quantity'] for i in st.session_state.cart.values())
cart_total = sum(i['price'] * i['quantity'] for i in st.session_state.cart.values())

st.markdown(f"""
<div class="app-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
            <span style="background:rgba(0, 245, 212, 0.15); color:#00f5d4; font-size:11px; font-weight:800; padding:0.3rem 0.8rem; border-radius:1rem; border:1px solid rgba(0, 245, 212, 0.3); text-transform:uppercase;">
                🟢 Live In-Store System
            </span>
            <h2 style="margin:0.4rem 0 0 0; color:#ffffff; font-weight:900; letter-spacing:-0.03em;">🛒 Scan & Go — Queue-Free Retail</h2>
            <p style="margin:0.2rem 0 0 0; color:#94a3b8; font-size:13px;">Selected Outlet: <b>📍 {outlet_display}</b></p>
        </div>
        <div style="background:rgba(15, 23, 42, 0.9); border:1px solid rgba(255, 255, 255, 0.1); padding:0.75rem 1.25rem; border-radius:1rem; text-align:right;">
            <div style="font-size:10px; text-transform:uppercase; color:#94a3b8; font-weight:800;">Active Shopping Cart</div>
            <div style="font-size:16px; font-weight:900; color:#00f5d4;">${cart_total:.2f} ({cart_count} items)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# 🔐 COMMON AUTHENTICATION PAGE (AVAILABLE IN BOTH MODES)
# =============================================================================
if selected_page == "🔐 Account Sign In & Register":
    st.title("🔐 Authentication Portal")
    st.caption("Access the Scan & Go shopper terminal, pre-visit stock inspector, or merchant management console.")

    if st.session_state.user:
        st.success(f"✅ **You are signed in as:** `{st.session_state.user['email']}`")
        st.info("Select a destination below to enter the platform:")
        
        c_nav1, c_nav2, c_nav3 = st.columns(3)
        with c_nav1:
            if st.button("🏬 Discover Physical Outlets →", type="primary", use_container_width=True):
                st.session_state.customer_page = "🏬 Discover Physical Outlets"
                st.rerun()
        with c_nav2:
            if st.button("🔍 Inspect Pre-Visit Store Catalog →", use_container_width=True):
                st.session_state.customer_page = "🔍 Pre-Visit Store Catalog"
                st.rerun()
        with c_nav3:
            if st.button("📊 Launch Merchant Analytics →", use_container_width=True):
                st.session_state.merchant_page = "📊 Sales Analytics & AI Engine"
                st.rerun()

        st.markdown("---")

    col_auth_left, col_auth_right = st.columns([1, 1])

    with col_auth_left:
        st.markdown("### ✨ Platform Capabilities")
        
        st.markdown("""
        <div class="auth-feature-card">
            <h4 style="margin:0; color:#00f5d4;">📱 Pre-Visit Stock Inspection</h4>
            <p style="margin:0.3rem 0 0 0; color:#94a3b8; font-size:12px;">Browse physical store shelf inventory, check live In-Stock / Out-of-Stock status, view special discounts, and see new arrivals before physically visiting.</p>
        </div>
        
        <div class="auth-feature-card">
            <h4 style="margin:0; color:#38bdf8;">🎥 In-Store Barcode & QR Scan & Go</h4>
            <p style="margin:0.3rem 0 0 0; color:#94a3b8; font-size:12px;">Scan product barcodes or QR codes directly using your phone's camera, add items to cart, and checkout instantly — bypassing cash register lines.</p>
        </div>

        <div class="auth-feature-card">
            <h4 style="margin:0; color:#a855f7;">🔮 Scikit-Learn AI Demand Forecasting</h4>
            <p style="margin:0.3rem 0 0 0; color:#94a3b8; font-size:12px;">Merchant analytics dashboard equipped with Random Forest inventory demand forecasting and customer churn risk classification.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### ⚡ 1-Click Fast Login")
        c_demo1, c_demo2 = st.columns(2)
        with c_demo1:
            if st.button("✨ Demo Customer", type="primary", use_container_width=True):
                db = get_db()
                u = db.query(User).filter(User.email == "customer@scango.com").first()
                if u:
                    st.session_state.user = {"id": u.id, "email": u.email, "role": u.role}
                    st.session_state.customer_page = "🏬 Discover Physical Outlets"
                    st.rerun()
                db.close()
        with c_demo2:
            if st.button("⚡ Demo Merchant", use_container_width=True):
                db = get_db()
                u = db.query(User).filter(User.email == "test@scango.com").first()
                if u:
                    st.session_state.user = {"id": u.id, "email": u.email, "role": u.role}
                    st.session_state.merchant_page = "🏢 Outlets Management"
                    st.rerun()
                db.close()

    with col_auth_right:
        tab_login, tab_reg = st.tabs(["Sign In", "Create Account"])
        
        with tab_login:
            login_email = st.text_input("Email Address", value="customer@scango.com", key="login_email_input")
            login_pass = st.text_input("Password", value="password123", type="password", key="login_pass_input")
            
            if st.button("Sign In to App", type="primary", use_container_width=True):
                db = get_db()
                user = db.query(User).filter(User.email == login_email).first()
                if user and verify_password(login_pass, user.hashed_password):
                    st.session_state.user = {"id": user.id, "email": user.email, "role": user.role}
                    if user.role == "merchant":
                        st.session_state.merchant_page = "🏢 Outlets Management"
                    else:
                        st.session_state.customer_page = "🏬 Discover Physical Outlets"
                    st.success("Successfully authenticated!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                db.close()

        with tab_reg:
            reg_email = st.text_input("New Email Address", key="reg_email_input")
            reg_pass = st.text_input("New Password", type="password", key="reg_pass_input")
            reg_role = st.selectbox("Register Account Type:", ["Shopper / Customer", "Store Merchant"])

            if st.button("Create Account", use_container_width=True):
                if reg_email and reg_pass:
                    db = get_db()
                    existing = db.query(User).filter(User.email == reg_email).first()
                    if existing:
                        st.error("User with this email already exists.")
                    else:
                        role_str = "merchant" if "Merchant" in reg_role else "shopper"
                        new_u = User(merchant_id=1, email=reg_email, hashed_password=hash_password(reg_pass), role=role_str)
                        db.add(new_u)
                        db.commit()
                        db.refresh(new_u)
                        st.session_state.user = {"id": new_u.id, "email": new_u.email, "role": new_u.role}
                        if role_str == "merchant":
                            st.session_state.merchant_page = "🏢 Outlets Management"
                        else:
                            st.session_state.customer_page = "🏬 Discover Physical Outlets"
                        st.success("Account created successfully!")
                        st.rerun()
                    db.close()
                else:
                    st.warning("Please enter email and password.")


# =============================================================================
# 👥 CUSTOMER PORTAL EXPERIENCE
# =============================================================================
elif app_mode == "👥 Customer Experience Portal":

    # -------------------------------------------------------------------------
    # 1. DISCOVER PHYSICAL OUTLETS
    # -------------------------------------------------------------------------
    if selected_page == "🏬 Discover Physical Outlets":
        st.title("🏬 Discover Physical Outlets")
        st.caption("Locate physical retail stores, check opening hours, and inspect live inventory *before* visiting.")

        db = get_db()
        outlets = db.query(Outlet).all()
        db.close()

        search_query = st.text_input("🔎 Search outlets by store name or city:", placeholder="e.g. Downtown, Metro Center, or Greenfield")

        if search_query:
            outlets = [o for o in outlets if search_query.lower() in o.name.lower() or search_query.lower() in o.city.lower()]

        cols = st.columns(len(outlets) if outlets else 1)
        for idx, o in enumerate(outlets):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="outlet-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; font-size:18px; color:#fff;">🏪 {o.name}</h3>
                        <span style="background:rgba(0, 245, 212, 0.15); color:#00f5d4; font-size:11px; font-weight:800; padding:0.2rem 0.5rem; border-radius:0.5rem;">⭐ 4.9</span>
                    </div>
                    <p style="color:#94a3b8; font-size:13px; margin:0.5rem 0;">📍 {o.address}, {o.city}</p>
                    <p style="color:#00f5d4; font-weight:bold; font-size:13px; margin:0.2rem 0;">⚡ {o.distance_km} km away • 🟢 Open ({o.opening_hours})</p>
                    <p style="color:#cbd5e1; font-size:12px; margin:0.2rem 0 1rem 0;">📞 {o.contact_phone}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🔍 Inspect Live Inventory ({o.name[:16]}...)", key=f"select_o_{o.id}", type="primary", use_container_width=True):
                    st.session_state.active_outlet_id = o.id
                    st.session_state.customer_page = "🔍 Pre-Visit Store Catalog"
                    st.rerun()

    # -------------------------------------------------------------------------
    # 2. PRE-VISIT STORE CATALOG & STOCK INSPECTOR
    # -------------------------------------------------------------------------
    elif selected_page == "🔍 Pre-Visit Store Catalog":
        db = get_db()
        active_outlet = db.query(Outlet).filter(Outlet.id == st.session_state.active_outlet_id).first()
        if not active_outlet:
            active_outlet = db.query(Outlet).first()
            st.session_state.active_outlet_id = active_outlet.id

        st.title(f"🔍 Live Shelf Inventory: {active_outlet.name}")
        st.caption("Check real-time stock levels, prices, special discounts, and new product launches before physically visiting.")

        st.info("💡 **Pre-Visit Notice:** Home delivery is disabled. Use this catalog to verify stock availability, then physically visit the store to Scan & Go!")

        all_outlets = db.query(Outlet).all()
        selected_o_id = st.selectbox(
            "Select Physical Outlet:",
            options=[o.id for o in all_outlets],
            format_func=lambda x: next(o.name for o in all_outlets if o.id == x),
            index=[o.id for o in all_outlets].index(st.session_state.active_outlet_id)
        )
        if selected_o_id != st.session_state.active_outlet_id:
            st.session_state.active_outlet_id = selected_o_id
            st.rerun()

        tab_all, tab_instock, tab_offers, tab_new = st.tabs([
            "📦 All Products", 
            "✅ In-Stock Only", 
            "🏷️ Special Offers & Discounts", 
            "🔥 New Product Launches"
        ])

        products = db.query(Product).filter(Product.outlet_id == st.session_state.active_outlet_id).all()
        db.close()

        def render_product_grid(prod_list):
            if not prod_list:
                st.warning("No products matching this filter criteria at this outlet.")
                return

            p_cols = st.columns(3)
            for idx, p in enumerate(prod_list):
                with p_cols[idx % 3]:
                    st.markdown(f"#### {p.name}")
                    
                    badges_html = ""
                    if p.is_in_stock and p.stock > 0:
                        badges_html += f'<span class="badge-in-stock">🟢 In Stock ({p.stock} left)</span> '
                    else:
                        badges_html += '<span class="badge-out-stock">🔴 Out of Stock</span> '

                    if p.discount_percent > 0:
                        badges_html += f'<span class="badge-offer">🏷️ {p.discount_percent:.0f}% OFF</span> '
                    if p.is_new_launch:
                        badges_html += '<span class="badge-new">🔥 New Launch</span>'

                    st.markdown(badges_html, unsafe_allow_html=True)
                    
                    if p.discount_percent > 0:
                        st.markdown(f"**Price:** :green[**${p.price:.2f}**] ~(${p.original_price:.2f}~)")
                    else:
                        st.markdown(f"**Price:** **${p.price:.2f}**")

                    st.caption(f"Category: {p.category} | Barcode: `{p.barcode}`")
                    st.markdown("---")

        with tab_all:
            render_product_grid(products)
        with tab_instock:
            render_product_grid([p for p in products if p.is_in_stock and p.stock > 0])
        with tab_offers:
            render_product_grid([p for p in products if p.discount_percent > 0])
        with tab_new:
            render_product_grid([p for p in products if p.is_new_launch])

    # -------------------------------------------------------------------------
    # 3. IN-STORE SCAN & GO TERMINAL
    # -------------------------------------------------------------------------
    elif selected_page == "📱 In-Store Scan & Go":
        db = get_db()
        active_outlet = db.query(Outlet).filter(Outlet.id == st.session_state.active_outlet_id).first()
        db.close()

        st.title(f"📱 In-Store Scan & Go Terminal ({active_outlet.name if active_outlet else 'Store #01'})")
        st.caption("Point your camera at product barcodes or QR codes while physically inside the store.")

        if not st.session_state.user:
            st.warning("Please Sign In or use 1-Click Demo Customer Login in the sidebar.")
            st.stop()

        if st.session_state.last_scanned:
            st.success(f"🛒 **Scanned & Added to Cart:** {st.session_state.last_scanned}")

        st.markdown("### ⚡ Store Quick Barcode Scan Chips")
        db = get_db()
        outlet_products = db.query(Product).filter(Product.outlet_id == st.session_state.active_outlet_id).all()
        db.close()

        chip_cols = st.columns(len(outlet_products) if outlet_products else 1)
        for idx, p in enumerate(outlet_products):
            with chip_cols[idx % len(chip_cols)]:
                if st.button(f"{p.name[:14]}.. (${p.price:.2f})", key=f"chip_scan_{p.id}", use_container_width=True):
                    add_to_cart_by_barcode(p.barcode, st.session_state.active_outlet_id)
                    st.rerun()

        st.markdown("---")
        st.markdown("### 🎥 Camera & Image QR Code / Barcode Decoder")
        
        c_cam, c_file = st.columns([1, 1])

        with c_cam:
            st.markdown("#### Option A: Live Camera Viewfinder")
            camera_photo = st.camera_input("Point camera directly at QR Code or Barcode:")
            if camera_photo:
                decoded_text = decode_qr_or_barcode(camera_photo)
                if decoded_text:
                    st.success(f"🎉 **QR / Barcode Decoded:** `{decoded_text}`")
                    add_to_cart_by_barcode(decoded_text, st.session_state.active_outlet_id)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ No barcode recognized in camera photo. Align code inside frame and take photo again.")

        with c_file:
            st.markdown("#### Option B: Upload Image File")
            up_file = st.file_uploader("Upload QR Code or Barcode image file (PNG, JPG, WEBP):", type=["png", "jpg", "jpeg", "webp"])
            if up_file:
                decoded_text = decode_qr_or_barcode(up_file)
                if decoded_text:
                    st.success(f"🎉 **Uploaded Image Decoded:** `{decoded_text}`")
                    add_to_cart_by_barcode(decoded_text, st.session_state.active_outlet_id)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ Could not decode QR / Barcode from uploaded image file.")

    # -------------------------------------------------------------------------
    # 4. CART & CHECKOUT WITH UPI PAYMENTS
    # -------------------------------------------------------------------------
    elif selected_page == "🛒 Cart & Checkout":
        st.title("🛒 Active Shopping Cart & Checkout")

        if not st.session_state.cart:
            st.info("Your cart is currently empty. Visit **📱 In-Store Scan & Go** to scan items.")
        else:
            cart_list = []
            for pid, item in st.session_state.cart.items():
                total = item['price'] * item['quantity']
                cart_list.append({
                    "Product Name": item['name'],
                    "Barcode / QR": item['barcode'],
                    "Unit Price ($)": f"${item['price']:.2f}",
                    "Quantity": item['quantity'],
                    "Total ($)": f"${(item['price'] * item['quantity']):.2f}"
                })

            df_cart = pd.DataFrame(cart_list)
            st.dataframe(df_cart, use_container_width=True)

            subtotal = sum(i['price'] * i['quantity'] for i in st.session_state.cart.values())
            tax = subtotal * 0.18
            grand_total = subtotal + tax

            st.markdown(f"### Grand Total: :green[**${grand_total:.2f}**] (includes 18% Sales Tax)")
            
            payment_method = st.selectbox(
                "Select Payment Method", 
                [
                    "📲 UPI (Google Pay / PhonePe / Paytm / BHIM)", 
                    "💳 Credit / Debit Card", 
                    "🍎 Apple Pay / Google Wallet", 
                    "👛 Store App Wallet"
                ]
            )

            upi_vpa = ""
            if "UPI" in payment_method:
                st.markdown("#### 📲 Instant UPI Payment Option")
                c_upi1, c_upi2 = st.columns([1, 1])
                
                with c_upi1:
                    upi_app = st.radio("Select UPI Provider:", ["Google Pay", "PhonePe", "Paytm", "BHIM UPI", "Custom VPA"], horizontal=True)
                    upi_vpa = st.text_input("Enter your UPI ID / VPA:", value="user@okaxis" if upi_app=="Google Pay" else ("user@ybl" if upi_app=="PhonePe" else "user@paytm"))
                    st.caption("Example: `user@okaxis`, `user@ybl`, `user@paytm`, `9876543210@upi`")

                with c_upi2:
                    st.markdown("##### Dynamic UPI Payment QR Code")
                    upi_uri = f"upi://pay?pa=scango.merchant@okaxis&pn=ScanAndGoRetail&am={grand_total:.2f}&cu=INR"
                    qr_img = qrcode.make(upi_uri)
                    img_buf = io.BytesIO()
                    qr_img.save(img_buf, format="PNG")
                    st.image(img_buf.getvalue(), caption=f"Scan with {upi_app} to Pay ${grand_total:.2f}", width=180)

            if st.button(f"💳 Pay ${grand_total:.2f} & Generate Digital Receipt", type="primary", use_container_width=True):
                db = get_db()
                txn = Transaction(
                    user_id=st.session_state.user['id'] if st.session_state.user else 1,
                    merchant_id=1,
                    outlet_id=st.session_state.active_outlet_id,
                    subtotal=subtotal,
                    discount=0.0,
                    tax=tax,
                    total_amount=grand_total,
                    payment_method=f"UPI ({upi_vpa})" if "UPI" in payment_method else payment_method
                )
                db.add(txn)
                db.commit()
                db.refresh(txn)

                for item in st.session_state.cart.values():
                    ci = CartItem(transaction_id=txn.id, product_id=item['product_id'], quantity=item['quantity'], unit_price=item['price'])
                    db.add(ci)
                    prod = db.query(Product).filter(Product.id == item['product_id']).first()
                    if prod:
                        prod.stock = max(0, prod.stock - item['quantity'])
                        if prod.stock == 0:
                            prod.is_in_stock = False

                db.commit()
                db.close()

                st.balloons()
                st.success(f"🎉 Payment Successful via {payment_method}! Receipt #{txn.id} generated & store inventory updated.")
                st.session_state.cart = {}

    # -------------------------------------------------------------------------
    # 5. PURCHASE & RECEIPT HISTORY
    # -------------------------------------------------------------------------
    elif selected_page == "🧾 Purchase & Receipt History":
        st.title("🧾 Digital Receipt & Purchase History")

        if not st.session_state.user:
            st.warning("Please sign in to view purchase history.")
            st.stop()

        db = get_db()
        txns = db.query(Transaction).filter(Transaction.user_id == st.session_state.user['id']).all()
        db.close()

        if not txns:
            st.info("No past receipts found. Complete a checkout in the **In-Store Scan & Go** terminal.")
        else:
            for t in txns[::-1]:
                with st.expander(f"🧾 Digital Receipt #{t.id} — ${t.total_amount:.2f} ({t.created_at.strftime('%b %d, %Y %I:%M %p')})"):
                    st.write(f"**Payment Method:** {t.payment_method}")
                    st.write(f"**Status:** {t.status.upper()}")
                    st.write(f"**Total Amount Paid:** ${t.total_amount:.2f}")


# =============================================================================
# 🏢 MERCHANT CONSOLE EXPERIENCE
# =============================================================================
else:

    # -------------------------------------------------------------------------
    # 1. OUTLETS MANAGEMENT
    # -------------------------------------------------------------------------
    if selected_page == "🏢 Outlets Management":
        st.title("🏢 Outlets Management Console")
        st.caption("Add and manage physical retail store outlets.")

        db = get_db()
        outlets = db.query(Outlet).all()
        db.close()

        col_list, col_add = st.columns([2, 1])

        with col_list:
            st.markdown("### Active Physical Outlets")
            for o in outlets:
                st.markdown(f"""
                <div class="outlet-card">
                    <h4>🏪 {o.name}</h4>
                    <p style="color:#94a3b8; font-size:12px;">Address: {o.address}, {o.city} | Phone: {o.contact_phone}</p>
                    <p style="color:#00f5d4; font-size:12px; font-weight:bold;">Distance: {o.distance_km} km | Hours: {o.opening_hours}</p>
                </div>
                """, unsafe_allow_html=True)

        with col_add:
            st.markdown("### ➕ Add New Store Outlet")
            o_name = st.text_input("Store Outlet Name:", placeholder="e.g. Uptown Hypermarket #04")
            o_addr = st.text_input("Street Address:", placeholder="e.g. 500 Market Blvd")
            o_city = st.text_input("City:", value="Central City")
            o_dist = st.number_input("Distance (km):", min_value=0.1, value=1.5)
            
            if st.button("Save New Outlet", type="primary", use_container_width=True):
                if o_name and o_addr:
                    db = get_db()
                    new_outlet = Outlet(merchant_id=1, name=o_name, address=o_addr, city=o_city, distance_km=o_dist)
                    db.add(new_outlet)
                    db.commit()
                    db.close()
                    st.success("New store outlet created successfully!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # 2. PRODUCT & BARCODE CATALOG
    # -------------------------------------------------------------------------
    elif selected_page == "📦 Product & Barcode Catalog":
        st.title("📦 Product & Barcode Management")

        db = get_db()
        outlets = db.query(Outlet).all()

        col_p_list, col_p_add = st.columns([2, 1])

        with col_p_list:
            st.markdown("### Existing Products Catalog")
            prods = db.query(Product).all()
            p_data = [{
                "ID": p.id,
                "Outlet": next((o.name[:15] for o in outlets if o.id == p.outlet_id), "Store #01"),
                "Name": p.name,
                "Barcode": p.barcode,
                "Price ($)": f"${p.price:.2f}",
                "Stock": p.stock,
                "Status": "In Stock" if p.is_in_stock else "Out of Stock",
                "New Launch": "🔥 Yes" if p.is_new_launch else "No"
            } for p in prods]

            st.dataframe(pd.DataFrame(p_data), use_container_width=True)

        with col_p_add:
            st.markdown("### ➕ Add Product to Outlet")
            target_o_id = st.selectbox("Select Target Outlet:", options=[o.id for o in outlets], format_func=lambda x: next(o.name for o in outlets if o.id == x))
            p_name = st.text_input("Product Name:")
            p_price = st.number_input("Selling Price ($):", min_value=0.5, value=4.99)
            p_stock = st.number_input("Initial Stock Quantity:", min_value=0, value=50)
            p_cat = st.text_input("Category:", value="Beverages")
            p_code = st.text_input("Barcode Number:", value=f"890{int(time.time())}"[-12:])

            if st.button("Create Product & Generate Barcode", type="primary", use_container_width=True):
                if p_name:
                    new_p = Product(
                        merchant_id=1,
                        outlet_id=target_o_id,
                        sku=f"SKU-{p_code[-4:]}",
                        name=p_name,
                        price=p_price,
                        original_price=p_price,
                        stock=p_stock,
                        is_in_stock=p_stock > 0,
                        category=p_cat,
                        barcode=p_code
                    )
                    db.add(new_p)
                    db.commit()
                    st.success(f"Product '{p_name}' added to outlet!")
                    st.rerun()
        db.close()

    # -------------------------------------------------------------------------
    # 3. STOCK & OFFERS MANAGER
    # -------------------------------------------------------------------------
    elif selected_page == "⚡ Stock & Offers Manager":
        st.title("⚡ Stock & Promotional Offers Control")
        st.caption("Update stock quantities, toggle availability status, configure discounts, and tag new launches.")

        db = get_db()
        prods = db.query(Product).all()

        st.markdown("### Update Stock, Offers & Launches:")
        for p in prods:
            with st.expander(f"📦 {p.name} (Barcode: {p.barcode} | Current Stock: {p.stock})"):
                c_s1, c_s2, c_s3, c_s4 = st.columns(4)
                
                with c_s1:
                    new_stock = st.number_input(f"Stock Qty", min_value=0, value=p.stock, key=f"stk_{p.id}")
                with c_s2:
                    in_stock_toggle = st.checkbox("Mark In Stock", value=p.is_in_stock, key=f"chk_stk_{p.id}")
                with c_s3:
                    discount = st.number_input("Discount %", min_value=0.0, max_value=80.0, value=p.discount_percent, key=f"disc_{p.id}")
                with c_s4:
                    new_launch_toggle = st.checkbox("🔥 Tag New Launch", value=p.is_new_launch, key=f"chk_launch_{p.id}")

                if st.button("Save Changes", key=f"btn_save_p_{p.id}"):
                    p.stock = new_stock
                    p.is_in_stock = in_stock_toggle and (new_stock > 0)
                    p.discount_percent = discount
                    if discount > 0:
                        p.price = round(p.original_price * (1 - (discount / 100)), 2)
                    else:
                        p.price = p.original_price
                    p.is_new_launch = new_launch_toggle
                    db.commit()
                    st.success(f"Updated {p.name}!")
                    st.rerun()
        db.close()

    # -------------------------------------------------------------------------
    # 4. SALES ANALYTICS & AI ENGINE
    # -------------------------------------------------------------------------
    elif selected_page == "📊 Sales Analytics & AI Engine":
        st.title("📊 Merchant Analytics & AI Forecast Engine")

        db = get_db()
        txns = db.query(Transaction).all()
        db.close()

        total_rev = sum(t.total_amount for t in txns) if txns else 14850.50

        k1, k2, k3 = st.columns(3)
        k1.metric("Gross Revenue", f"${total_rev:,.2f}", "+18.4%")
        k2.metric("Total Transactions", f"{len(txns)} Orders", "Live Completed")
        k3.metric("Scans / Hour", "42.5", "+5.1%")

        st.markdown("---")
        st.markdown("### 🔮 Scikit-Learn 7-Day Sales Forecast")
        df_forecast = ml_pipeline.forecast_next_ndays(7)
        fig_ml = px.area(df_forecast, x='Date', y='Predicted Sales ($)', title="AI Predicted Sales Demand ($)", color_discrete_sequence=['#a855f7'])
        fig_ml.update_layout(template="plotly_dark", height=320)
        st.plotly_chart(fig_ml, use_container_width=True)
