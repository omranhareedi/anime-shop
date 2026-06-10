from app import db
from app.models import Category, Product, Vendor, User


def seed_database():
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@narmo.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    if Category.query.first() is not None and Product.query.count() > 0:
        return

    categories = [
        Category(name='Figures', slug='figures', description='High-quality anime figures and statues'),
        Category(name='Apparel', slug='apparel', description='Anime-themed clothing and accessories'),
        Category(name='Posters', slug='posters', description='Anime posters and wall art'),
        Category(name='Accessories', slug='accessories', description='Keychains, badges, and more'),
        Category(name='Manga', slug='manga', description='Japanese comics and graphic novels'),
    ]
    db.session.add_all(categories)
    db.session.commit()

    vendors = [
        Vendor(name='OtakuCraft', slug='otakucraft', rating=4.9,
               description='Hand-crafted figures and statues from master artisans.',
               email='hello@otakucraft.com', location='Osaka, Japan', is_active=True),
        Vendor(name='WeebWear', slug='weebwear', rating=4.3,
               description='Streetwear meets anime. Premium apparel for fans.',
               email='support@weebwear.com', location='Tokyo, Japan', is_active=True),
        Vendor(name='PosterPulse', slug='posterpulse', rating=4.7,
               description='High-definition posters and wall art prints.',
               email='info@posterpulse.com', location='Kyoto, Japan', is_active=True),
        Vendor(name='MangaMart', slug='mangamart', rating=4.6,
               description='Your one-stop shop for manga and light novels.',
               email='orders@mangamart.com', location='Shinjuku, Japan', is_active=True),
    ]
    db.session.add_all(vendors)
    db.session.commit()

    products = [
        Product(name='Naruto Shippuden - Sage Mode Figure',
                slug='naruto-sage-mode-figure',
                description='Highly detailed 25cm figure of Naruto in Sage Mode.',
                price=49.99, stock=15, genre='Action',
                category_id=categories[0].id, vendor_id=vendors[0].id, is_featured=True,
                image_url='naruto_figure.jpg'),
        Product(name='Attack on Titan - Levi Ackerman Figure',
                slug='levi-ackerman-figure',
                description='Premium PVC figure of Captain Levi.',
                price=59.99, stock=10, genre='Action',
                category_id=categories[0].id, vendor_id=vendors[0].id, is_featured=True,
                image_url='levi_figure.jpg'),
        Product(name='Demon Slayer - Tanjiro Hoodie',
                slug='tanjiro-hoodie',
                description='Comfortable cotton hoodie with Tanjiro Kamado design.',
                price=44.99, stock=25, genre='Adventure',
                category_id=categories[1].id, vendor_id=vendors[1].id, is_featured=True,
                image_url='tanjiro_hoodie.jpg'),
        Product(name='My Hero Academia - Class 1-A T-Shirt',
                slug='mha-class-1a-tshirt',
                description='Official MHA t-shirt featuring all your favorite heroes.',
                price=24.99, stock=30, genre='Action',
                category_id=categories[1].id, vendor_id=vendors[1].id, is_featured=True,
                image_url='mha_tshirt.jpg'),
        Product(name='Spy x Family - Anya Poster',
                slug='anya-poster',
                description='Colorful A2 poster of Anya Forger. Waku Waku!',
                price=14.99, stock=50, genre='Comedy',
                category_id=categories[2].id, vendor_id=vendors[2].id, is_featured=True,
                image_url='anya_poster.jpg'),
        Product(name='Jujutsu Kaisen - Gojo Poster',
                slug='gojo-poster',
                description='Limited edition A2 poster of Satoru Gojo.',
                price=19.99, stock=40, genre='Action',
                category_id=categories[2].id, vendor_id=vendors[2].id, is_featured=True,
                image_url='gojo_poster.jpg'),
        Product(name='Chainsaw Man - Pochita Keychain',
                slug='pochita-keychain',
                description='Cute acrylic keychain of Pochita.',
                price=8.99, stock=100, genre='Action',
                category_id=categories[3].id, vendor_id=vendors[0].id, is_featured=False,
                image_url='pochita_keychain.jpg'),
        Product(name='One Piece - Straw Hat Pins Set',
                slug='straw-hat-pins',
                description='Set of 10 enamel pins of the Straw Hat crew.',
                price=18.99, stock=35, genre='Adventure',
                category_id=categories[3].id, vendor_id=vendors[0].id, is_featured=False,
                image_url='straw_hat_pins.jpg'),
        Product(name='Demon Slayer Vol.1 - Manga',
                slug='demon-slayer-vol1',
                description='First volume of the hit series Demon Slayer.',
                price=9.99, stock=60, genre='Adventure',
                category_id=categories[4].id, vendor_id=vendors[3].id, is_featured=False,
                image_url='demon_slayer_vol1.jpg'),
        Product(name='Attack on Titan Vol.1 - Manga',
                slug='aot-vol1',
                description='First volume of the phenomenon Attack on Titan.',
                price=9.99, stock=45, genre='Action',
                category_id=categories[4].id, vendor_id=vendors[3].id, is_featured=True,
                image_url='aot_vol1.jpg'),
        Product(name='Fullmetal Alchemist - Ed & Al Figure',
                slug='fmab-brothers-figure',
                description='Detailed figure of the Elric brothers.',
                price=69.99, stock=8, genre='Adventure',
                category_id=categories[0].id, vendor_id=vendors[0].id, is_featured=False,
                image_url='fmab_figure.jpg'),
        Product(name='Cowboy Bebop - Spike Spiegel Poster',
                slug='spike-poster',
                description='A2 poster featuring Spike Spiegel.',
                price=16.99, stock=20, genre='Sci-Fi',
                category_id=categories[2].id, vendor_id=vendors[2].id, is_featured=False,
                image_url='spike_poster.jpg'),
    ]
    db.session.add_all(products)
    db.session.commit()
