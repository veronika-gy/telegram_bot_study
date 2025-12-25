from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Ticket

# --- Пользователи ---
async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, telegram_id: int, name: str, group: str, phone: str = None) -> User:
    new_user = User(telegram_id=telegram_id, name=name, group=group, phone=phone)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def get_all_users(session: AsyncSession):
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()

# --- Заявки ---
async def create_ticket(session: AsyncSession, user_id: int, text: str, photo: str = None) -> Ticket:
    new_ticket = Ticket(user_id=user_id, text=text, photo=photo)
    session.add(new_ticket)
    await session.commit()
    await session.refresh(new_ticket)
    return new_ticket

async def get_tickets_by_user(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Ticket).where(Ticket.user_id == user_id).order_by(Ticket.created_at.desc())
    )
    return result.scalars().all()

async def get_all_tickets(session: AsyncSession):
    result = await session.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    return result.scalars().all()

async def get_tickets_by_status(session: AsyncSession, status: str):
    result = await session.execute(
        select(Ticket).where(Ticket.status == status).order_by(Ticket.created_at.desc())
    )
    return result.scalars().all()

async def update_ticket_status(session: AsyncSession, ticket_id: int, new_status: str):
    result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket:
        ticket.status = new_status
        await session.commit()
    return ticket



