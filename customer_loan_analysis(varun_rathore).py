# EDA CASE STUDY ON LOAN DATASET

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import warnings   
warnings.filterwarnings('ignore')

#Reading the Dataset
loanData=pd.read_csv(r"/content/loan.csv")
loanData.head()

#Dataset Inspection
print(loanData.info())
print(loanData.dtypes)
print(loanData.shape)
# loanData has 111 featurs and 39717 rows    
#     74 features are float64
#     13 features are int64 and
#     24 features are object datatypes


#Data Cleaning
loanData.isnull().sum(axis=0)

print(round(100*(loanData.isnull().sum()/len(loanData.index)),2))

#total missing columns
null_col= loanData.isnull().sum()
null_col = null_col[null_col.values >(0.3*len(loanData))]
null_col.count()

plt.figure(figsize=(20,5))
null_col.plot(kind='bar',color='green')
plt.title('More than 30% NA values')
plt.show()

#Droping columns
loanData.drop(loanData.iloc[:,53:111],axis=1,inplace=True)

loanData.shape

null_col= loanData.isnull().sum()
null_col = null_col[null_col.values >(0.3*len(loanData))]
null_col.count()

print(round(100*(loanData.isnull().sum()/len(loanData.index)),2))

#Still, there are some null values
loanData=loanData.drop(['mths_since_last_major_derog','next_pymnt_d','mths_since_last_record','mths_since_last_delinq','desc'],axis=1)
round(100*(loanData.isnull().sum()/len(loanData.index)),2)

#drop column on the base of unique values
uniq = loanData.nunique()
uniq = uniq[uniq.values ==1]
uniq.count

loanData=loanData.drop(['pymnt_plan','initial_list_status','collections_12_mths_ex_med','policy_code','application_type'],axis=1)
loanData.shape

irr_colm = ["id","member_id","zip_code"]
loanData.drop(labels = irr_colm, axis =1, inplace=True)
print(loanData.shape)

#Replace NA with 0
#       becoz self employed people has NA marked

print(loanData.emp_length.unique())
loanData.emp_length.fillna('0',inplace=True)
loanData.emp_length.replace(['n/a'],'Self-Employed',inplace=True)
print(loanData.emp_length.unique())

#Remove unnecessary values(not needed in analysis)
unncolms=(loanData.loan_status.value_counts()*100)/len(loanData)
unncolms

unncolms = unncolms[(unncolms < 1.5)]
loanData.drop(labels = loanData[loanData.loan_status.isin(unncolms.index)].index, inplace=True)
print(loanData.shape)
print(loanData.loan_status.unique())

# Univeriate Analysis
#   -continuous variables
loanData['loan_amnt'].describe()

plt.figure(figsize=(10,6))
plt.subplot(121)
plt.boxplot(loanData['loan_amnt'])

plt.subplot(122)
plt.violinplot(loanData['loan_amnt']);

loanData['int_rate'] = loanData['int_rate'].replace("%","", regex=True).astype(float)
loanData['int_rate'].describe()
plt.figure(figsize=(15,8))
plt.subplot(121)
plt.boxplot(loanData['int_rate'])
plt.subplot(122)
sns.distplot(loanData['int_rate'],color='red');

loanData["annual_inc"] = loanData['annual_inc'].apply(pd.to_numeric)

loanData.annual_inc.describe()

out = loanData["annual_inc"].quantile(0.995)
loanData = loanData[loanData["annual_inc"] < out]
loanData["annual_inc"].describe()

plt.figure(figsize=(15,8))
plt.subplot(121)
plt.boxplot(loanData['annual_inc'],showfliers=False)
plt.subplot(122)
sns.distplot(loanData['annual_inc'],color='violet');

# categorical variables :
def univariate(df,col,vartype,hue =None):
    if vartype == 1:
        temp = pd.Series(data = hue)
        fig, ax = plt.subplots()
        width = len(df[col].unique()) + 6 + 4*len(temp.unique())
        fig.set_size_inches(width , 7)
        ax = sns.countplot(data = df, x= col, order=df[col].value_counts().index,hue = hue) 
        if len(temp.unique()) > 0:
            for p in ax.patches:
                ax.annotate('{:1.1f}%'.format((p.get_height()*100)/float(len(loanData))), (p.get_x()+0.05, p.get_height()+20))  
        else:
            for p in ax.patches:
                ax.annotate(p.get_height(), (p.get_x()+0.32, p.get_height()+20)) 
        del temp
    else:
        exit  
    plt.show()

univariate(df=loanData,col='loan_status',vartype=1)

univariate(df=loanData,col='purpose',vartype=1,hue='loan_status')

univariate(df=loanData,col='term',vartype=1,hue='loan_status')

plt.figure(figsize=(20,10))
year_wise =loanData.groupby(by= [loanData.issue_d])[['loan_status']].count()
year_wise.rename(columns={"loan_status": "count"},inplace=True)
ax =year_wise.plot(figsize=(20,8))
year_wise.plot(kind='bar',figsize=(20,8),ax = ax)
plt.show()

#Bivariate Analysis
loan_corr= loanData.corr()
loan_corr

plt.figure(figsize=(25,12))
sns.boxplot(data =loanData, x='purpose', y='loan_amnt', hue ='loan_status')
plt.title(' Loan Amount vs Purpose of Loan ',weight='bold',fontsize=15)
plt.xlabel('purpose',fontsize=10)
plt.ylabel('loan_amnt',fontsize=10)

plt.figure(figsize=(20,25))
sns.heatmap(loan_corr, 
            xticklabels=loan_corr.columns.values,
            yticklabels=loan_corr.columns.values,annot= True);

#Now , we are creating a pivot table for better understanding.
lonestat_piv=loanData.pivot_table(index=['loan_status','purpose','emp_length'],values='loan_amnt',aggfunc=('count')).reset_index()
loanstat_piv=loanData.loc[loanData['loan_status']=='Charged Off']

plt.figure(figsize=(20,15))
sns.boxplot(x='emp_length',y='loan_amnt',hue='purpose',data=loanstat_piv)
plt.title('Employment Length vs Loan Amount for different pupose',fontsize=20,weight="bold")
plt.xlabel('Employment Length',fontsize=18)
plt.ylabel('Loan Amount',fontsize=18)

#Calculating probablity of Charged Off
def crosstab(df,col):
    
    crosstab = pd.crosstab(df[col], df['loan_status'],margins=True)
    crosstab['Probability_Charged Off'] = round((crosstab['Charged Off']/crosstab['All']),3)
    crosstab = crosstab[0:-1]
    return crosstab

def bivariate_prob(df,col,stacked= True):

    plotCrosstab = crosstab(df,col)
    
    linePlot = plotCrosstab[['Probability_Charged Off']]      
    barPlot =  plotCrosstab.iloc[:,0:2]
    ax = linePlot.plot(figsize=(20,8), marker='o',color = 'b')
    ax2 = barPlot.plot(kind='bar',ax = ax,rot=1,secondary_y=True,stacked=stacked)
    ax.set_title(df[col].name.title()+' vs Probability Charge Off',fontsize=20,weight="bold")
    ax.set_xlabel(df[col].name.title(),fontsize=14)
    ax.set_ylabel('Probability of Charged off',color = 'b',fontsize=14)
    ax2.set_ylabel('Number of Applicants',color = 'g',fontsize=14)
    plt.show()

emp_length = crosstab(loanData,'emp_length')
display(emp_length)

bivariate_prob(df =loanData,col ='emp_length')

filter_states = loanData.addr_state.value_counts()
filter_states = filter_states[(filter_states < 10)]

loan_filter_states = loanData.drop(labels = loanData[loanData.addr_state.isin(filter_states.index)].index)

states = crosstab(loan_filter_states,'addr_state')
display(states.tail(20))

bivariate_prob(df =loan_filter_states,col ='addr_state')

purpose = crosstab(loanData,'purpose')
display(purpose)

bivariate_prob(df =loanData,col ='purpose',stacked=False)

annual_inc = crosstab(loanData,'annual_inc')
display('annual_inc')

bivariate_prob(df =loanData,col ='annual_inc')

int_rate=crosstab(loanData,'int_rate')
display('int_rate')

bivariate_prob(df =loanData,col ='int_rate')
