INSERT INTO ianlewis.blog_post 
    (
     id,
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
    post_ID as id,
    1 AS author_id,
    post_urltitle AS slug,
    post_title AS title,
    IF(itpr_content_prerendered IS NOT NULL,itpr_content_prerendered,post_content) as content,
    "html" AS markup_type,
    IF(cat_blog_ID=5,"en","jp") AS locale,
    "" AS tags,
    IF(post_status="published",1,0) AS active,
    post_datestart AS pub_date,
    post_datecreated AS create_date 
from ianlewis_b2evo.evo_items__item
    LEFT JOIN ianlewis_b2evo.evo_categories 
        ON post_main_cat_ID = cat_ID
    LEFT OUTER JOIN ianlewis_b2evo.evo_items__prerendering
        ON post_ID = itpr_itm_ID AND itpr_format = "htmlbody"
WHERE cat_blog_ID = 5 OR cat_blog_ID = 14;

insert into ianlewis.tagging_tag
    (
     id,
     name
    )
select
    tag_ID,
    tag_name
from ianlewis_b2evo.evo_items__tag;

insert into ianlewis.tagging_taggeditem
    (
     tag_id,
     content_type_id,
     object_id
    )
select 
    itag_tag_ID,
    (select id from ianlewis.django_content_type where name = 'post'),
    itag_itm_ID
from ianlewis_b2evo.evo_items__itemtag;

-- Lifestream
insert into ianlewis.lifestream_feed
  (
   id,
   name,
   url,
   domain,
   fetchable,
   plugin_class_name
  )
select
  feed_id as id,
  feed_title as name,
  feed_url as url,
  feed_domain as domain,
  (IF feed_status="active",1,0) as fetchable,
  NULL as plugin_class_name
from ianlewis_swtcron.feeds;

select
  ID as id,
  item_feed_id as feed_id,
  item_date as date,
  item_title as title,
  item_content as content,
  "text/html" as content_type,
  item_content as clean_content,
  "" as author,
  item_permalink as permalink,  
  IF(item_status == "publish",1,0) as published
  -- TODO: parse out video/picture data
from ianlewis_swtcron.items;
