from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, CheckConstraint, Column, Date, Enum, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Table, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Discount(Base):
    __tablename__ = 'discount'
    __table_args__ = (
        CheckConstraint('percentage > 0::numeric AND percentage < 100::numeric', name='discount_percentage_check'),
        PrimaryKeyConstraint('_id', name='discount_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Enum('student', 'school', 'senior', 'military', name='discount_name'), nullable=False)
    percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(4, 2))

    ticket: Mapped[list['Ticket']] = relationship('Ticket', back_populates='fk_discount')


class Movie(Base):
    __tablename__ = 'movie'
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='movie_duration_minutes_check'),
        PrimaryKeyConstraint('_id', name='movie_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    director: Mapped[Optional[str]] = mapped_column(String(50))
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    movie_version: Mapped[list['MovieVersion']] = relationship('MovieVersion', back_populates='fk_movie')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        CheckConstraint('price >= 0::numeric', name='product_price_check'),
        PrimaryKeyConstraint('_id', name='product_pkey'),
        UniqueConstraint('barcode', name='product_barcode_key'),
        UniqueConstraint('name', name='product_name_key')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    barcode: Mapped[Optional[str]] = mapped_column(String(50))

    product_sale: Mapped[list['ProductSale']] = relationship('ProductSale', back_populates='fk_product')


class Region(Base):
    __tablename__ = 'region'
    __table_args__ = (
        PrimaryKeyConstraint('_id', name='region_pkey'),
        UniqueConstraint('name', name='region_name_key')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    cinema: Mapped[list['Cinema']] = relationship('Cinema', back_populates='fk_region')
    term: Mapped[list['Term']] = relationship('Term', back_populates='fk_region')


class SpecialOffer(Base):
    __tablename__ = 'special_offer'
    __table_args__ = (
        CheckConstraint('amount > 0::numeric', name='special_offer_amount_check'),
        CheckConstraint('end_time IS NULL OR end_time > start_time', name='special_offer_time_check'),
        PrimaryKeyConstraint('_id', name='special_offer_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=0), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    fk_ticket: Mapped[list['Ticket']] = relationship('Ticket', secondary='ticket_special_offer', back_populates='fk_special_offer')


class TicketType(Base):
    __tablename__ = 'ticket_type'
    __table_args__ = (
        CheckConstraint('price > 0::numeric', name='ticket_type_price_check'),
        PrimaryKeyConstraint('_id', name='ticket_type_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Enum('standard', 'reduced', name='ticket_type_name'), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    ticket: Mapped[list['Ticket']] = relationship('Ticket', back_populates='fk_ticket_type')


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint('account_create_date <= CURRENT_DATE', name='user_account_create_date_check'),
        CheckConstraint('birthdate <= CURRENT_DATE', name='user_birthdate_check'),
        CheckConstraint('char_length(name::text) > 0', name='user_name_check'),
        CheckConstraint('char_length(surname::text) > 0', name='user_surname_check'),
        CheckConstraint('char_length(username::text) >= 3', name='user_username_check'),
        CheckConstraint("email::text ~~ '%%@%%'::text", name='user_email_check'),
        CheckConstraint('last_login_time IS NULL OR last_login_time >= account_create_date AND last_login_time <= CURRENT_TIMESTAMP', name='user_check'),
        PrimaryKeyConstraint('_id', name='user_pkey'),
        UniqueConstraint('email', name='user_email_key'),
        UniqueConstraint('username', name='user_username_key')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    birthdate: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    account_create_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    last_login_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0), server_default=text('NULL::timestamp without time zone'))


class Version(Base):
    __tablename__ = 'version'
    __table_args__ = (
        PrimaryKeyConstraint('_id', name='version_pkey'),
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language: Mapped[str] = mapped_column(Enum('polish', 'english', 'spanish', 'german', name='languages'), nullable=False)
    subtitles: Mapped[str] = mapped_column(Enum('polish', 'english', 'spanish', 'german', name='languages'), nullable=False)
    format: Mapped[str] = mapped_column(Enum('2D', '3D', 'IMAX', name='movie_format'), nullable=False)

    movie_version: Mapped[list['MovieVersion']] = relationship('MovieVersion', back_populates='fk_version')


class Cinema(Base):
    __tablename__ = 'cinema'
    __table_args__ = (
        CheckConstraint('building_number > 0', name='cinema_building_number_check'),
        ForeignKeyConstraint(['fk_region_id'], ['region._id'], ondelete='CASCADE', name='c_fk_region'),
        PrimaryKeyConstraint('_id', name='cinema_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_region_id: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    street: Mapped[Optional[str]] = mapped_column(String(50))
    building_number: Mapped[Optional[int]] = mapped_column(Integer)

    fk_region: Mapped['Region'] = relationship('Region', back_populates='cinema')
    fk_movie_version: Mapped[list['MovieVersion']] = relationship('MovieVersion', secondary='cinema_movie_version', back_populates='fk_cinema')
    employment: Mapped[list['Employment']] = relationship('Employment', back_populates='fk_cinema')
    room: Mapped[list['Room']] = relationship('Room', back_populates='fk_cinema')
    product_sale: Mapped[list['ProductSale']] = relationship('ProductSale', back_populates='fk_cinema')


class Client(User):
    __tablename__ = 'client'
    __table_args__ = (
        ForeignKeyConstraint(['_id'], ['user._id'], ondelete='CASCADE', name='c_fk_client_user_id'),
        PrimaryKeyConstraint('_id', name='client_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)

    payment: Mapped[list['Payment']] = relationship('Payment', back_populates='fk_client')


class License(Movie):
    __tablename__ = 'license'
    __table_args__ = (
        CheckConstraint('cost > 0::numeric', name='license_cost_check'),
        CheckConstraint('end_date >= start_date', name='license_date_check'),
        ForeignKeyConstraint(['_id'], ['movie._id'], ondelete='CASCADE', name='c_id'),
        PrimaryKeyConstraint('_id', name='license_pkey'),
        UniqueConstraint('license_number', name='license_license_number_key')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    license_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))


class MovieVersion(Base):
    __tablename__ = 'movie_version'
    __table_args__ = (
        ForeignKeyConstraint(['fk_movie_id'], ['movie._id'], ondelete='CASCADE', name='c_fk_movie'),
        ForeignKeyConstraint(['fk_version_id'], ['version._id'], ondelete='CASCADE', name='c_fk_version'),
        PrimaryKeyConstraint('_id', name='movie_version_pkey'),
        UniqueConstraint('fk_movie_id', 'fk_version_id', name='no_duplicate_movie_version')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_movie_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_version_id: Mapped[int] = mapped_column(Integer, nullable=False)

    fk_cinema: Mapped[list['Cinema']] = relationship('Cinema', secondary='cinema_movie_version', back_populates='fk_movie_version')
    fk_movie: Mapped['Movie'] = relationship('Movie', back_populates='movie_version')
    fk_version: Mapped['Version'] = relationship('Version', back_populates='movie_version')
    screening: Mapped[list['Screening']] = relationship('Screening', back_populates='fk_movie_version')


class RegionalManager(User):
    __tablename__ = 'regional_manager'
    __table_args__ = (
        ForeignKeyConstraint(['_id'], ['user._id'], ondelete='CASCADE', name='c_fk_user_id'),
        PrimaryKeyConstraint('_id', name='regional_manager_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)

    term: Mapped[list['Term']] = relationship('Term', back_populates='fk_manager')


class Worker(User):
    __tablename__ = 'worker'
    __table_args__ = (
        CheckConstraint('char_length(bank_account_number::text) = 26', name='worker_bank_account_number_check'),
        CheckConstraint('char_length(pesel_number::text) = 11', name='worker_pesel_number_check'),
        CheckConstraint('salary_month > 0::numeric', name='worker_salary_month_check'),
        ForeignKeyConstraint(['_id'], ['user._id'], ondelete='CASCADE', name='fk_worker_user_id'),
        PrimaryKeyConstraint('_id', name='worker_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pesel_number: Mapped[str] = mapped_column(String(11), nullable=False)
    bank_account_number: Mapped[str] = mapped_column(String(26), nullable=False)
    salary_month: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    employment: Mapped[list['Employment']] = relationship('Employment', back_populates='fk_worker')
    shift: Mapped[list['Shift']] = relationship('Shift', back_populates='fk_worker')


t_cinema_movie_version = Table(
    'cinema_movie_version', Base.metadata,
    Column('fk_cinema_id', Integer, primary_key=True),
    Column('fk_movie_version_id', Integer, primary_key=True),
    ForeignKeyConstraint(['fk_cinema_id'], ['cinema._id'], ondelete='CASCADE', name='c_fk_cinema_id'),
    ForeignKeyConstraint(['fk_movie_version_id'], ['movie_version._id'], ondelete='CASCADE', name='c_fk_movie_version_id'),
    PrimaryKeyConstraint('fk_cinema_id', 'fk_movie_version_id', name='cinema_movie_version_pkey')
)


class Employment(Base):
    __tablename__ = 'employment'
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR end_date >= start_date', name='employment_date_check'),
        ForeignKeyConstraint(['fk_cinema_id'], ['cinema._id'], ondelete='CASCADE', name='c_fk_employment_cinema_id'),
        ForeignKeyConstraint(['fk_worker_id'], ['worker._id'], ondelete='CASCADE', name='c_fk_employment_worker_id'),
        PrimaryKeyConstraint('_id', name='employment_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_cinema_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    fk_cinema: Mapped['Cinema'] = relationship('Cinema', back_populates='employment')
    fk_worker: Mapped['Worker'] = relationship('Worker', back_populates='employment')


class Payment(Base):
    __tablename__ = 'payment'
    __table_args__ = (
        CheckConstraint('amount >= 0::numeric', name='payment_amount_check'),
        ForeignKeyConstraint(['fk_client_id'], ['client._id'], name='c_fk_client_id'),
        PrimaryKeyConstraint('_id', name='payment_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(Enum('cash', 'card', 'blik', 'online', 'voucher', name='payment_type'), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fk_client_id: Mapped[Optional[int]] = mapped_column(Integer)

    fk_client: Mapped[Optional['Client']] = relationship('Client', back_populates='payment')
    product_sale: Mapped[list['ProductSale']] = relationship('ProductSale', back_populates='fk_payment')
    ticket: Mapped[list['Ticket']] = relationship('Ticket', back_populates='fk_payment')


class Room(Base):
    __tablename__ = 'room'
    __table_args__ = (
        CheckConstraint('number > 0', name='room_number_check'),
        ForeignKeyConstraint(['fk_cinema_id'], ['cinema._id'], ondelete='CASCADE', name='c_fk_cinema'),
        PrimaryKeyConstraint('_id', name='room_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_cinema_id: Mapped[int] = mapped_column(Integer, nullable=False)
    number: Mapped[Optional[int]] = mapped_column(Integer)

    fk_cinema: Mapped['Cinema'] = relationship('Cinema', back_populates='room')
    screening: Mapped[list['Screening']] = relationship('Screening', back_populates='fk_room')
    seat: Mapped[list['Seat']] = relationship('Seat', back_populates='fk_room')


class Service(Worker):
    __tablename__ = 'service'
    __table_args__ = (
        ForeignKeyConstraint(['_id'], ['worker._id'], ondelete='CASCADE', name='c_fk_service_id'),
        PrimaryKeyConstraint('_id', name='service_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Shift(Base):
    __tablename__ = 'shift'
    __table_args__ = (
        CheckConstraint('end_time IS NULL OR end_time > start_time', name='shift_time_check'),
        ForeignKeyConstraint(['fk_worker_id'], ['worker._id'], ondelete='CASCADE', name='c_fk_shift_worker_id'),
        PrimaryKeyConstraint('_id', name='shift_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=0), nullable=False)
    type: Mapped[str] = mapped_column(Enum('cashier', 'usher', 'cleaning', 'projection', 'technical_support', name='shift_type'), nullable=False)
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    fk_worker: Mapped['Worker'] = relationship('Worker', back_populates='shift')


class Supervisor(Worker):
    __tablename__ = 'supervisor'
    __table_args__ = (
        ForeignKeyConstraint(['_id'], ['worker._id'], ondelete='CASCADE', name='c_fk_supervisor_worker_id'),
        PrimaryKeyConstraint('_id', name='supervisor_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Term(Base):
    __tablename__ = 'term'
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR end_date >= start_date', name='term_date_check'),
        ForeignKeyConstraint(['fk_manager_id'], ['regional_manager._id'], ondelete='CASCADE', name='c_fk_manager_id'),
        ForeignKeyConstraint(['fk_region_id'], ['region._id'], ondelete='CASCADE', name='c_fk_region_id'),
        PrimaryKeyConstraint('_id', name='term_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_region_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_manager_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    fk_manager: Mapped['RegionalManager'] = relationship('RegionalManager', back_populates='term')
    fk_region: Mapped['Region'] = relationship('Region', back_populates='term')


class ProductSale(Base):
    __tablename__ = 'product_sale'
    __table_args__ = (
        CheckConstraint('time_of_sale <= CURRENT_TIMESTAMP', name='product_sale_time_of_sale_check'),
        ForeignKeyConstraint(['fk_cinema_id'], ['cinema._id'], ondelete='CASCADE', name='c_fk_cinema_id'),
        ForeignKeyConstraint(['fk_payment_id'], ['payment._id'], ondelete='CASCADE', name='c_fk_payment_id'),
        ForeignKeyConstraint(['fk_product_id'], ['product._id'], ondelete='CASCADE', name='c_fk_product_id'),
        PrimaryKeyConstraint('_id', name='product_sale_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_payment_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_cinema_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    time_of_sale: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=0), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    fk_cinema: Mapped['Cinema'] = relationship('Cinema', back_populates='product_sale')
    fk_payment: Mapped['Payment'] = relationship('Payment', back_populates='product_sale')
    fk_product: Mapped['Product'] = relationship('Product', back_populates='product_sale')


class Screening(Base):
    __tablename__ = 'screening'
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='screening_time_check'),
        ForeignKeyConstraint(['fk_movie_version_id'], ['movie_version._id'], ondelete='CASCADE', name='c_fk_movie_version_id'),
        ForeignKeyConstraint(['fk_room_id'], ['room._id'], ondelete='CASCADE', name='c_fk_room_id'),
        PrimaryKeyConstraint('_id', name='screening_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_room_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_movie_version_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=0), nullable=False)
    end_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=0), nullable=False)

    fk_movie_version: Mapped['MovieVersion'] = relationship('MovieVersion', back_populates='screening')
    fk_room: Mapped['Room'] = relationship('Room', back_populates='screening')
    ticket: Mapped[list['Ticket']] = relationship('Ticket', back_populates='fk_screening')


class Seat(Base):
    __tablename__ = 'seat'
    __table_args__ = (
        CheckConstraint('seat_num > 0', name='seat_seat_num_check'),
        ForeignKeyConstraint(['fk_room_id'], ['room._id'], ondelete='CASCADE', name='c_fk_room_id'),
        PrimaryKeyConstraint('_id', name='seat_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_room_id: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_num: Mapped[int] = mapped_column(Integer, nullable=False)

    fk_room: Mapped['Room'] = relationship('Room', back_populates='seat')
    ticket: Mapped[list['Ticket']] = relationship('Ticket', back_populates='fk_seat')


class Ticket(Base):
    __tablename__ = 'ticket'
    __table_args__ = (
        ForeignKeyConstraint(['fk_discount_id'], ['discount._id'], name='c_fk_discount_id'),
        ForeignKeyConstraint(['fk_payment_id'], ['payment._id'], name='c_fk_payment_id'),
        ForeignKeyConstraint(['fk_screening_id'], ['screening._id'], ondelete='CASCADE', name='c_fk_screening_id'),
        ForeignKeyConstraint(['fk_seat_id'], ['seat._id'], ondelete='CASCADE', name='c_fk_seat_id'),
        ForeignKeyConstraint(['fk_ticket_type_id'], ['ticket_type._id'], ondelete='CASCADE', name='c_fk_ticket_type_id'),
        PrimaryKeyConstraint('_id', name='ticket_pkey')
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_ticket_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_screening_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_seat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    qr_code: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(Enum('used', 'valid', 'reserved', 'payment_pending', 'free', name='ticket_status'), nullable=False, server_default=text("'free'::ticket_status"))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    fk_discount_id: Mapped[Optional[int]] = mapped_column(Integer)
    fk_payment_id: Mapped[Optional[int]] = mapped_column(Integer)

    fk_special_offer: Mapped[list['SpecialOffer']] = relationship('SpecialOffer', secondary='ticket_special_offer', back_populates='fk_ticket')
    fk_discount: Mapped[Optional['Discount']] = relationship('Discount', back_populates='ticket')
    fk_payment: Mapped[Optional['Payment']] = relationship('Payment', back_populates='ticket')
    fk_screening: Mapped['Screening'] = relationship('Screening', back_populates='ticket')
    fk_seat: Mapped['Seat'] = relationship('Seat', back_populates='ticket')
    fk_ticket_type: Mapped['TicketType'] = relationship('TicketType', back_populates='ticket')


t_ticket_special_offer = Table(
    'ticket_special_offer', Base.metadata,
    Column('fk_ticket_id', Integer, primary_key=True),
    Column('fk_special_offer_id', Integer, primary_key=True),
    ForeignKeyConstraint(['fk_special_offer_id'], ['special_offer._id'], ondelete='CASCADE', name='c_fk_special_offer_id'),
    ForeignKeyConstraint(['fk_ticket_id'], ['ticket._id'], ondelete='CASCADE', name='c_fk_ticket_id'),
    PrimaryKeyConstraint('fk_ticket_id', 'fk_special_offer_id', name='ticket_special_offer_pkey')
)
