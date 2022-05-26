create table profiles
(
    id bigint not null primary key,
    balance decimal(14, 2) not null
);

create table balancehistory
(
    id int auto_increment primary key,
    profile_id bigint not null,
    balance decimal(14, 2) not null,
    time datetime not null,
    tag text null,
    constraint balancehistory_ibfk_1 foreign key (profile_id) references profiles (id)
);

create table companies
(
    id int auto_increment primary key,
    profile_id bigint         null,
    name       text           not null,
    worth      decimal(14, 2) not null,
    constraint companies_ibfk_1 foreign key (profile_id) references profiles (id)
);

create table shares
(
    id int auto_increment primary key,
    profile_id bigint not null,
    company_id int    not null,
    num_shares bigint not null,
    constraint shares_ibfk_1 foreign key (profile_id) references profiles (id),
    constraint shares_ibfk_2 foreign key (company_id) references companies (id)
);

create table worthhistory
(
    id int auto_increment primary key,
    company_id int not null,
    worth decimal(14, 2) not null,
    time datetime not null,
    tag text null,
    constraint worthhistory_ibfk_1 foreign key (company_id) references companies (id)
);