import random
import logging
from faker import Faker
from datetime import timedelta
from typing import List, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.engine import Engine

random.seed(87)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')


# Initialize Faker and SQLAlchemy base
fake = Faker()
Base = declarative_base()

# Define enriched models
class Member(Base):
    """
    Represents a member in the e-commerce system.
    """
    __tablename__ = 'members'
    member_id = Column(Integer, primary_key=True)
    member_name = Column(String)
    email = Column(String)
    join_date = Column(DateTime)
    member_level = Column(String)
    referrer_id = Column(Integer, ForeignKey('members.member_id'), nullable=True)
    gender = Column(String)
    birth_year = Column(Integer)
    country = Column(String)
    is_active = Column(Boolean)

class Item(Base):
    """
    Represents an item available for purchase.
    """
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String)
    category = Column(String)
    subcategory = Column(String)
    brand = Column(String)
    price = Column(Float)
    stock_quantity = Column(Integer)
    rating = Column(Float)
    is_active = Column(Boolean)
    created_at = Column(DateTime)

class Campaign(Base):
    """
    Represents a marketing campaign with discounts.
    """
    __tablename__ = 'campaigns'
    campaign_id = Column(Integer, primary_key=True)
    campaign_name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    discount_rate = Column(Float)
    channel = Column(String)
    description = Column(String)

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.member_id'))
    campaign_id = Column(Integer, ForeignKey('campaigns.campaign_id'), nullable=True)
    discount_rate = Column(Float)
    final_price = Column(Float)
    payment_method = Column(String)
    transaction_time = Column(DateTime)

    member = relationship('Member')
    campaign = relationship('Campaign')
    items = relationship('TransactionItem', back_populates='transaction')

class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    transaction_id = Column(Integer, ForeignKey('transactions.transaction_id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), primary_key=True)
    quantity = Column(Integer)
    unit_price = Column(Float)

    transaction = relationship('Transaction', back_populates='items')
    item = relationship('Item')

class DataGenerator:
    """
    A class to generate synthetic data for the e-commerce database.
    """

    def __init__(self, session: Session, fake: Faker):
        """
        Initializes the DataGenerator with a SQLAlchemy session and a Faker instance.

        Args:
            session (Session): The SQLAlchemy session object.
            fake (Faker): The Faker instance for generating fake data.
        """
        self.session = session
        self.fake = fake

    def generate_members(self, num_members: int = 100) -> List[Member]:
        """
        Generates a specified number of synthetic member records.
        
        Args:
            num_members (int): The number of item records to generate. Defaults to 100.
        
        Returns:
            list: A list of generated Member objects.
        """
        logging.info(f"Generating {num_members} members...")
        members = []
        for i in range(1, num_members + 1):
            referrers = [m.member_id for m in members if m.member_id != i]
            referrer = random.choice(referrers) if referrers and random.random() < 0.3 else None
            
            member = Member(
                member_id=i,
                member_name=self.fake.name(),
                email=self.fake.unique.email(),
                join_date=self.fake.date_time_between(start_date='-3y', end_date='now'),
                member_level=random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
                referrer_id=referrer,
                gender=random.choice(['Male', 'Female', 'Unknown']),
                birth_year=random.randint(1960, 2007),
                country=random.choice(['Taiwan', 'Japan', 'Korea', 'USA']),
                is_active=random.choices([True, False], weights=[0.8, 0.2])[0]
            )
            members.append(member)
        self.session.add_all(members)
        return members

    def generate_items(self, num_items: int = 30) -> List[Item]:
        """
        Generates a specified number of synthetic item records.
        
        Args:
            num_items (int): The number of item records to generate. Defaults to 30.
        
        Returns:
            list: A list of generated Item objects.
        """
        logging.info(f"Generating {num_items} items...")
        category_structure = {
            'Electronics': {
                'subcategories': ['Laptop', 'Smartphone', 'Headphones', 'Tablet'],
                'brands': ['Apple', 'Samsung', 'Sony', 'ASUS', 'Logitech']
            },
            'Apparel': {
                'subcategories': ['T-Shirt', 'Jeans', 'Sneakers', 'Jacket'],
                'brands': ['Nike', 'Adidas', 'Uniqlo', 'Levi\'s', 'North Face']
            },
            'Home & Kitchen': {
                'subcategories': ['Sofa', 'Dining Table', 'Cookware Set', 'Lamp'],
                'brands': ['IKEA', 'Philips', 'Tefal', 'Panasonic']
            },
            'Sports & Outdoors': {
                'subcategories': ['Backpack', 'Running Shoes', 'Yoga Mat', 'Bicycle'],
                'brands': ['Nike', 'Adidas', 'Decathlon', 'Giant']
            },
            'Beauty & Personal Care': {
                'subcategories': ['Shampoo', 'Face Wash', 'Lipstick', 'Perfume'],
                'brands': ['L\'Oréal', 'Dove', 'Nivea', 'Maybelline']
            }
        }
        items = []
        for i in range(1, num_items + 1):
            category = random.choice(list(category_structure.keys()))
            subcategory = random.choice(category_structure[category]['subcategories'])
            brand = random.choice(category_structure[category]['brands'])

            item = Item(
                item_id=i,
                item_name=self.fake.word().capitalize() + " " + self.fake.word().capitalize(),
                category=category,
                subcategory=subcategory,
                brand=brand,
                price=round(random.uniform(10, 2000), 2),
                stock_quantity=random.randint(0, 500),
                rating=round(random.uniform(1, 5), 1),
                is_active=random.choice([True, True, False]),
                created_at=self.fake.date_time_between(start_date='-3y', end_date='now')
            )
            items.append(item)
        self.session.add_all(items)
        return items

    def generate_campaigns(self, num_campaigns: int = 5) -> List[Campaign]:
        """
        Generates a specified number of synthetic campaign records.

        Args:
            num_campaigns (int): The number of campaign records to generate. Defaults to 5.

        Returns:
            list: A list of generated Campaign objects.
        """
        logging.info(f"Generating {num_campaigns} campaigns...")
        campaigns = []
        for i in range(1, num_campaigns + 1):
            start = self.fake.date_time_between(start_date='-3y', end_date='now')
            end = start + timedelta(days=random.randint(7, 30))
            campaign = Campaign(
                campaign_id=i,
                campaign_name=self.fake.word().capitalize() + " Sale",
                start_date=start,
                end_date=end,
                discount_rate=round(random.uniform(5, 30), 2),
                channel=random.choice(['App', 'Website', 'Email', 'Social Media']),
                description=self.fake.sentence()
            )
            campaigns.append(campaign)
        self.session.add_all(campaigns)
        return campaigns

    def generate_transactions(self, members: List[Member], items: List[Item], campaigns: List[Campaign], num_transactions: int = 150) -> List[Transaction]:
        """
        Generates a specified number of synthetic transaction records.

        Args:
            members (list): A list of Member objects to link transactions to.
            items (list): A list of Item objects to link transactions to.
            campaigns (list): A list of Campaign objects to link transactions to (optional).
            num_transactions (int): The number of transaction records to generate. Defaults to 150.

        Returns:
            list: A list of generated Transaction objects.
        """
        logging.info(f"Generating {num_transactions} transactions...")
        transactions = []
        transaction_items = []
        for i in range(1, num_transactions + 1):
            member = random.choice(members)
            campaign = random.choice(campaigns) if random.random() < 0.3 else None
            discount = campaign.discount_rate if campaign else 0.0

            transaction = Transaction(
                transaction_id=i,
                member_id=member.member_id,
                campaign_id=campaign.campaign_id if campaign else None,
                discount_rate=discount,
                final_price=0.0, 
                payment_method=random.choice(['CreditCard', 'PayPal', 'ATM', 'LinePay']),
                transaction_time=self.fake.date_time_between(start_date='-1y', end_date='now')
            )
            self.session.add(transaction)
            self.session.flush()

            total_price = 0.0
            selected_items = random.sample(items, k=random.randint(1, 3))
            for item in selected_items:
                quantity = random.randint(1, 5)
                unit_price = item.price
                total_price += (unit_price * quantity)

                transaction_item = TransactionItem(
                    transaction_id=transaction.transaction_id,
                    item_id=item.item_id,
                    quantity=quantity,
                    unit_price=unit_price,
                )
                transaction_items.append(transaction_item)

            transaction.final_price = round(total_price * (100 - discount) / 100, 2)
            transactions.append(transaction)

        self.session.add_all(transaction_items)
        return transactions, transaction_items

def create_sql_engine(db_url: str = 'sqlite:///:memory:') -> Tuple[Engine, Session]:
    """
    Creates an SQLAlchemy engine, defines the database schema, and populates it with synthetic data.

    Args:
        db_url (str): The SQLAlchemy database URL. Defaults to an in-memory SQLite database.

    Returns:
        sqlalchemy.engine.base.Engine: The created SQLAlchemy engine.
        sqlalchemy.orm.session.Session: The created SQLAlchemy session.
    """
    # Create engine and session
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    logging.info(f"Database schema created at {db_url}.")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Instantiate the generator and generate data
    data_generator = DataGenerator(session, fake)
    members = data_generator.generate_members()
    items = data_generator.generate_items()
    campaigns = data_generator.generate_campaigns()
    transactions, transaction_items = data_generator.generate_transactions(members, items, campaigns)

    # Add all to session
    session.add_all(members + items + campaigns + transactions + transaction_items)
    logging.info("All generated data added to session and committed.")
    session.commit()
    
    return engine, session


if __name__ == '__main__':
    engine, session = create_sql_engine()

    members = session.execute(text("SELECT * FROM members LIMIT 3")).fetchall()
    print("\nMembers:")
    for row in members:
        print(dict(row._mapping))

    items = session.execute(text("SELECT * FROM items LIMIT 3")).fetchall()
    print("\nItems:")
    for row in items:
        print(dict(row._mapping))

    transactions = session.execute(text("SELECT * FROM transactions LIMIT 3")).fetchall()
    print("\nTransactions:")
    for row in transactions:
        print(dict(row._mapping))

    campaigns = session.execute(text("SELECT * FROM campaigns LIMIT 3")).fetchall()
    print("\nCampaigns:")
    for row in campaigns:
        print(dict(row._mapping))