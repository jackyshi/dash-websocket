hdls:()!();

.z.ws:{neg[.z.w].Q.s @[value;x;{`$ "'",x}]}

.z.wo:{show .z.w;hdls[.z.w]::.z.a;}
.z.wc:{show .z.w;hdls[.z.w]::.z.w _ hdls[.z.w];}


senddata:{
 qty:rand 1+til 4;
 total:rand 30+til 971;
 tip:rand 10+til 91;
 payType:rand `cash`tab`visa`mastercard`bitcoin;
 name:rand `Ben`Jarrod`Vijay`Aziz;
 spent:rand 1+til 151;
 yr:rand 2012+til 5;
 hs:key hdls;
 res:`qty`total`tip`payType`Name`Spent`Year`x!(qty;total;tip;payType;name;spent;yr;.z.T);
 if[not ()~ hs;{[h;r](neg h).j.j r}[;res] each hs]};
 
senddata2:{
    hs:key hdls;
    res:8?10;
    if[not ()~ hs;{[h;r](neg h).j.j r}[;res] each hs]};

.z.ts:{senddata2[]};

\t 1000