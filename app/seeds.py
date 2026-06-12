from app import db
from app.models import Category, Product, Vendor, User


def _get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        db.session.add(instance)
    return instance


def seed_database():
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@narmo.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    categories_data = [
        {'name': 'Figures', 'slug': 'figures', 'description': 'High-quality anime figures and statues'},
        {'name': 'Apparel', 'slug': 'apparel', 'description': 'Anime-themed clothing and accessories'},
        {'name': 'Posters', 'slug': 'posters', 'description': 'Anime posters and wall art'},
        {'name': 'Accessories', 'slug': 'accessories', 'description': 'Keychains, badges, and more'},
        {'name': 'Manga', 'slug': 'manga', 'description': 'Japanese comics and graphic novels'},
    ]
    categories = {}
    for cd in categories_data:
        cat = _get_or_create(Category, slug=cd['slug'])
        for k, v in cd.items():
            setattr(cat, k, v)
        categories[cat.slug] = cat
    db.session.commit()

    vendors_data = [
        {'name': 'OtakuCraft', 'slug': 'otakucraft', 'rating': 4.9,
         'description': 'Hand-crafted figures and statues from master artisans.',
         'email': 'hello@otakucraft.com', 'location': 'Osaka, Japan', 'is_active': True},
        {'name': 'WeebWear', 'slug': 'weebwear', 'rating': 4.3,
         'description': 'Streetwear meets anime. Premium apparel for fans.',
         'email': 'support@weebwear.com', 'location': 'Tokyo, Japan', 'is_active': True},
        {'name': 'PosterPulse', 'slug': 'posterpulse', 'rating': 4.7,
         'description': 'High-definition posters and wall art prints.',
         'email': 'info@posterpulse.com', 'location': 'Kyoto, Japan', 'is_active': True},
        {'name': 'MangaMart', 'slug': 'mangamart', 'rating': 4.6,
         'description': 'Your one-stop shop for manga and light novels.',
         'email': 'orders@mangamart.com', 'location': 'Shinjuku, Japan', 'is_active': True},
    ]
    vendors = {}
    for vd in vendors_data:
        ven = _get_or_create(Vendor, slug=vd['slug'])
        for k, v in vd.items():
            setattr(ven, k, v)
        vendors[ven.slug] = ven
    db.session.commit()

    products_data = [
        Product(name='Naruto Shippuden - Sage Mode Figure',
                slug='naruto-sage-mode-figure',
                description='Highly detailed 25cm figure of Naruto in Sage Mode.',
                price=49.99, stock=15, genre='Action',
                category_id=categories['figures'].id, vendor_id=vendors['otakucraft'].id, is_featured=True,
                image_url='Naruto_Shippuden-Sage_Mode_Figure.jpg'),
        Product(name='Attack on Titan - Levi Ackerman Figure',
                slug='levi-ackerman-figure',
                description='Premium PVC figure of Captain Levi.',
                price=59.99, stock=10, genre='Action',
                category_id=categories['figures'].id, vendor_id=vendors['otakucraft'].id, is_featured=True,
                image_url='Attack_on_Titan-Levi_Ackerman_Figure.jpg'),
        Product(name='Demon Slayer - Tanjiro Hoodie',
                slug='tanjiro-hoodie',
                description='Comfortable cotton hoodie with Tanjiro Kamado design.',
                price=44.99, stock=25, genre='Adventure',
                category_id=categories['apparel'].id, vendor_id=vendors['weebwear'].id, is_featured=True,
                image_url='Demon_Slayer-Tanjiro_Hoodie.jpg'),
        Product(name='My Hero Academia - Class 1-A T-Shirt',
                slug='mha-class-1a-tshirt',
                description='Official MHA t-shirt featuring all your favorite heroes.',
                price=24.99, stock=30, genre='Action',
                category_id=categories['apparel'].id, vendor_id=vendors['weebwear'].id, is_featured=True,
                image_url='My_Hero_Academia-Class_1-A_T-Shirt.jpg'),
        Product(name='Spy x Family - Anya Poster',
                slug='anya-poster',
                description='Colorful A2 poster of Anya Forger. Waku Waku!',
                price=14.99, stock=50, genre='Comedy',
                category_id=categories['posters'].id, vendor_id=vendors['posterpulse'].id, is_featured=True,
                image_url='Spy_x_Family_-_Anya_Poster.jpg'),
        Product(name='Jujutsu Kaisen - Gojo Poster',
                slug='gojo-poster',
                description='Limited edition A2 poster of Satoru Gojo.',
                price=19.99, stock=40, genre='Action',
                category_id=categories['posters'].id, vendor_id=vendors['posterpulse'].id, is_featured=True,
                image_url='Jujutsu_Kaisen_-_Gojo_Poster.jpg'),
        Product(name='Chainsaw Man - Pochita Keychain',
                slug='pochita-keychain',
                description='Cute acrylic keychain of Pochita.',
                price=8.99, stock=100, genre='Action',
                category_id=categories['accessories'].id, vendor_id=vendors['otakucraft'].id, is_featured=False,
                image_url='Chainsaw_Man_-_Pochita_Keychain.jpg'),
        Product(name='One Piece - Straw Hat Pins Set',
                slug='straw-hat-pins',
                description='Set of 10 enamel pins of the Straw Hat crew.',
                price=18.99, stock=35, genre='Adventure',
                category_id=categories['accessories'].id, vendor_id=vendors['otakucraft'].id, is_featured=False,
                image_url='One_Piece_-_Straw_Hat_Pins_Set.jpg'),
        Product(name='Demon Slayer Vol.1 - Manga',
                slug='demon-slayer-vol1',
                description='First volume of the hit series Demon Slayer.',
                price=9.99, stock=60, genre='Adventure',
                category_id=categories['manga'].id, vendor_id=vendors['mangamart'].id, is_featured=False,
                image_url='Demon_Slayer_Vol.1_-_Manga.jpg'),
        Product(name='Attack on Titan Vol.1 - Manga',
                slug='aot-vol1',
                description='First volume of the phenomenon Attack on Titan.',
                price=9.99, stock=45, genre='Action',
                category_id=categories['manga'].id, vendor_id=vendors['mangamart'].id, is_featured=True,
                image_url='Attack_on_Titan_Vol.1_-_Manga.jpg'),
        Product(name='Fullmetal Alchemist - Ed & Al Figure',
                slug='fmab-brothers-figure',
                description='Detailed figure of the Elric brothers.',
                price=69.99, stock=8, genre='Adventure',
                category_id=categories['figures'].id, vendor_id=vendors['otakucraft'].id, is_featured=False,
                image_url='Fullmetal_Alchemist_-_Ed__Al_Figure.jpg'),
        Product(name='Cowboy Bebop - Spike Spiegel Poster',
                slug='spike-poster',
                description='A2 poster featuring Spike Spiegel.',
                price=16.99, stock=20, genre='Sci-Fi',
                category_id=categories['posters'].id, vendor_id=vendors['posterpulse'].id, is_featured=False,
                image_url='Cowboy_Bebop_-_Spike_Spiegel_Poster.jpg'),
    ]
    removed_slugs = [
        'aot-eren-yeager-figure', 'aot-mikasa-ackerman-figure', 'aot-armored-titan-figure',
        'survey-corps-jacket', 'aot-scout-regiment-tee',
        'aot-colossal-titan-poster', 'aot-wall-maria-poster',
        'aot-3dmg-keychain', 'aot-patch-set',
        'aot-vol-2-manga', 'aot-vol-3-manga',
    ]
    for slug in removed_slugs:
        p = Product.query.filter_by(slug=slug).first()
        if p:
            db.session.delete(p)
    db.session.commit()
    for pd in products_data:
        existing = Product.query.filter_by(slug=pd.slug).first()
        if existing is None:
            db.session.add(pd)
    db.session.commit()
