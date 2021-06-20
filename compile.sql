
select 
  case when genvote="(Undecided)" then 0 when genvote="Democratic candidate" then 2 when genvote="Lean Democratic candidate" then 1 when genvote="Republican candidate" then -2 when genvote="Lean Republican candidate" then -1 else null end as ball_generic,

  case when govvote="(Undecided)" then 0 when govvote="Tom Wolf" then 2 when govvote="Lean Tom Wolf" then 1 when govvote="Scott Wagner" then -2 when govvote="Lean Scott Wagner" then -1 else null end as ball_gov,

  case when party="Democrat" then 1 else null end as is_dem,
  case when party="Republican" then 1 else null end as is_gop,
  case when party<>"Democrat" and party<>"Republican" then 1 else null end as is_npa,
   
  case when gender='Female' then 1 else null end as is_female, 
  case when gender='Male' then 1 else null end as is_male,
    
   age, 

   partisan_score

 from dfs;

