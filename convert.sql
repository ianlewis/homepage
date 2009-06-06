insert into ianlewis.blog_post 
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
    1 as author_id,
    if(post_urltitle is not null and post_urltitle != '', post_urltitle, concat('p', post_ID)) as slug,
    post_title as title,
    if(itpr_content_prerendered is not null,itpr_content_prerendered,post_content) as content,
    "html" as markup_type,
    if(cat_blog_ID=5,"en","jp") as locale,
    "" as tags,
    if(post_status="published",1,0) as active,
    post_datestart as pub_date,
    post_datecreated as create_date 
from test.evo_items__item
    left join test.evo_categories 
        on post_main_cat_ID = cat_ID
    left outer join test.evo_items__prerendering
        on post_ID = itpr_itm_ID and itpr_format = "htmlbody"
where cat_blog_ID = 5 or cat_blog_ID = 14;

insert into ianlewis.tagging_tag
    (
     id,
     name
    )
select
    tag_ID,
    LOWER(tag_name)
from test.evo_items__tag;

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
from test.evo_items__itemtag;

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
  if(feed_status="active",1,0) as fetchable,
  NULL as plugin_class_name
from test.feeds where feed_status = "active";

insert into ianlewis.lifestream_item
  (
   id,
   feed_id,
   date,
   title,
   content,
   content_type,
   clean_content,
   author,
   permalink,
   published,
   media_url,
   media_player_url,
   media_description
  )
select
  ID as id,
  item_feed_id as feed_id,
  FROM_UNIXTIME(item_date) as date,
  item_title as title,
  item_content as content,
  "text/html" as content_type,
  item_content as clean_content,
  "" as author,
  item_permalink as permalink,
  if(item_status = "publish",1,0) as published,
  if(LENGTH(@media_url:=substring(@substr:=replace(substring(item_data, @idx1:=locate(";", item_data, locate("\"image\"",item_data)+7)+1, locate(";", item_data, @idx1)-@idx1),'_m.jpg','.jpg'), @idx2:=locate(":", @substr, locate(":", @substr)+1)+2, locate("\"", @substr, @idx2)-@idx2)) > 0, @media_url, null) as media_url,
  if(LENGTH(@media_player_url:=substring(@substr:=replace(substring(item_data, @idx3:=locate(";", item_data, locate("\"player\"",item_data)+7)+1, locate(";", item_data, @idx3)-@idx3),'?v=','/v/'), @idx4:=locate(":", @substr, locate(":", @substr)+1)+2, locate("\"", @substr, @idx4)-@idx2)) > 0, @media_player_url, null) as media_player_url,
  item_content as media_description
from test.items 
    left join test.feeds on item_feed_id = feed_id
where item_title is not null
    and item_title != ''
    and item_status = "publish"
    and feed_status = "active";

insert ignore into ianlewis.tagging_tag
    (
     name
    )
select
    LOWER(slug)
from test.tags
where slug not like "%\%%";

insert into ianlewis.tagging_taggeditem
    (
     tag_id,
     content_type_id,
     object_id
    )
select 
    (select id from ianlewis.tagging_tag where name = LOWER(test.tags.slug)) as tag_id,
    (select id from ianlewis.django_content_type where name = 'item') as content_type_id,
    item_id
from test.tag_relationships
    left join test.tags 
        on test.tag_relationships.tag_id =
            test.tags.tag_id
where slug not like "%\%%";;
