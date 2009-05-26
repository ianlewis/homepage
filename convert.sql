INSERT INTO ianlewis.blog_post 
    (
     author_id,
     slug,
     title,
     content,
     markup_type,
     locale,
     tags,
     active,
     pub_date,
     create_date
    )
select 
    1 AS author_id,
    post_urltitle AS slug,
    post_title AS title,
    post_content as content,
    "html" AS markup_type,
    IF(cat_blog_ID=5,"en","jp") AS locale,
    "" AS tags,
    IF(post_status="published",1,0) AS active,
    post_datestart AS pub_date,
    post_datecreated AS create_date 
from ianlewis_b2evo.evo_items__item
    LEFT JOIN ianlewis_b2evo.evo_categories 
        ON post_main_cat_ID = cat_ID
WHERE cat_blog_ID = 5 OR cat_blog_ID = 14;
