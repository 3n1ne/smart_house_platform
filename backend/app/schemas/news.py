def serialize_news(news):
    return {
        "id": news.id,
        "author_id": news.author_id,
        "title": news.title,
        "content": news.content,
        "status": news.status,
        "published_at": news.published_at.isoformat() if news.published_at else None,
        "created_at": news.created_at.isoformat() if news.created_at else None,
        "updated_at": news.updated_at.isoformat() if news.updated_at else None,
        "author": {
            "id": news.author.id,
            "username": news.author.username,
            "real_name": news.author.real_name,
            "role": news.author.role.code if news.author.role else None,
        }
        if news.author
        else None,
    }
