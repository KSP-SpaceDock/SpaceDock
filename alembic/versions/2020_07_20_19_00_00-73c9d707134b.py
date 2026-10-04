"""Add ModVersion.download_count

Revision ID: 73c9d707134b
Revises: 1aa078e0fb7e
Create Date: 2020-07-20 19:00:00

"""

# revision identifiers, used by Alembic.
revision = '73c9d707134b'
down_revision = '1aa078e0fb7e'

from datetime import datetime
from alembic import op
import sqlalchemy as sa

Base = sa.orm.declarative_base()


class ModVersion(Base):  # type: ignore
    __tablename__ = 'modversion'
    id = sa.Column(sa.Integer, primary_key=True)
    download_count = sa.Column(sa.Integer, default=0)


class DownloadEvent(Base):  # type: ignore
    __tablename__ = 'downloadevent'
    id = sa.Column(sa.Integer, primary_key=True)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('modversion.id'))
    version = sa.orm.relationship('ModVersion',
                                  backref=sa.orm.backref('downloads', order_by="desc(DownloadEvent.created)"))
    created = sa.Column(sa.DateTime, default=datetime.now, index=True)
    downloads = sa.Column(sa.Integer, default=0)


def upgrade() -> None:
    op.add_column('modversion', sa.Column('download_count', sa.Integer()))

    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    for mod_version in session.query(ModVersion).all():
        mod_version.download_count = sum(evt.downloads
                                         for evt in mod_version.downloads)
    session.commit()


def downgrade() -> None:
    op.drop_column('modversion', 'download_count')
