# AB Testi ile Bidding Yöntemlerinin Dönüşümünün Karşılaştırılması
"""
İş Problemi:
Facebook kısa süre önce mevcut "maximumbidding" adı verilen
teklif verme türüne alternatif olarak yeni bir teklif türü olan
"average bidding"’i tanıttı.
Müşterilerimizden biri olan bombabomba.com, bu yeni özelliği test
etmeye karar verdi ve average bidding'inmaximumbidding'den
daha fazla dönüşüm getirip getirmediğini anlamak için bir A/B
testi yapmak istiyor.
A/B testi 1 aydır devam ediyor ve bombabomba.com şimdi sizden
bu A/B testinin sonuçlarını analiz etmenizi bekliyor.
Bombabomba.com için nihai başarı ölçütü Purchase'dır. Bu
nedenle, istatistiksel testler için Purchase metriğine
odaklanılmalıdır.

Veri Seti Hikayesi:
Bir firmanın web site bilgilerini içeren bu veri setinde
kullanıcıların gördükleri ve tıkladıkları reklam sayıları gibi
bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.
Kontrol ve Test grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleri
ab_testing.xlsx excel’inin ayrı sayfalarında yer almaktadır.
Kontrol grubuna Maximum Bidding, test grubuna Average
Bidding uygulanmıştır.

4 Değişken 40 Gözlem 26 KB
Impression: Reklam görüntüleme sayısı
Click: Görüntülenen reklama tıklama sayısı
Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
Earning: Satın alınan ürünler sonrası elde edilen kazanç
"""

# Görev 1: Veriyi Hazırlama ve Analiz Etme
import pandas as pd
from scipy import stats

pd.set_option("display.max_columns", None)
pd.set_option("display.width",300)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

# Adım 1: ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı
# değişkenlere atayınız.
control_group = pd.read_excel("ab_testing/ab_testing_data.xlsx", sheet_name="Control Group")
test_group = pd.read_excel("ab_testing/ab_testing_data.xlsx", sheet_name="Test Group")
control_group.head()
test_group.head()
control_group = control_group.loc[:, ~control_group.columns.str.contains("Unnamed")]
test_group = test_group.loc[:, ~test_group.columns.str.contains("Unnamed")]

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.
def check_df(dataframe, head=5):
    print("#################### Shape ####################")
    print(dataframe.shape)
    print("#################### Dtypes ####################")
    print(dataframe.dtypes)
    print("#################### NA ####################")
    print(dataframe.isnull().sum())
    print("#################### Head ####################")
    print(dataframe.head())
    print("#################### Tail ####################")
    print(dataframe.tail())
    print("#################### Describe ####################")
    print(dataframe.describe().T)

check_df(control_group)
check_df(test_group)

# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.
test_group["Group"] = "Test"
control_group["Group"] = "Control"
df = pd.concat([control_group, test_group], ignore_index=True)
df.head()

# Görev 2: A/B Testinin Hipotezinin Tanımlanması
# Adım 1: Hipotezi tanımlayınız.
# H0 : M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark yoktur.)
# H1 : M1!= M2  (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark vardır.)

# Adım 2: Kontrol ve test grubu için purchase (kazanç) ortalamalarını analiz ediniz.
df.groupby("Group")["Purchase"].mean()

# Görev 3: Hipotez Testinin Gerçekleştirilmesi
# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.
# Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.
# Kontrol ve test grubunun normallik varsayımına uyup uymadığını  Purchase değişkeni üzerinden ayrı ayrı test ediniz.
# Normallik Varsayımı :
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır.
# p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ
# Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu ? Elde edilen p-value değerlerini yorumlayınız.
pvalue_test = stats.shapiro(df.loc[df["Group"] == "Test", "Purchase"])[1]
pvalue_control = stats.shapiro(df.loc[df["Group"] == "Control", "Purchase"])[1]
print(f"p-value Test Group= {pvalue_test}    p-value Control Group {pvalue_control}")
# p-value Test Group= 0.15413342416286469    p-value Control Group 0.5891125202178955
# H0 reddedilemez. Normallik varsayımı sağlanmaktadır.

# Varyans Homojenliği :
# H0: Varyanslar homojendir.
# H1: Varyanslar homojen Değildir.
# p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ
# Kontrol ve test grubu için varyans homojenliğinin sağlanıp sağlanmadığını Purchase değişkeni üzerinden test ediniz.
# Test sonucuna göre normallik varsayımı sağlanıyor mu? Elde edilen p-value değerlerini yorumlayınız.
pvalue = stats.levene(df.loc[df["Group"] == "Test", "Purchase"],
                      df.loc[df["Group"] == "Control", "Purchase"])[1]
print(pvalue) # 0.108285882718748 => H0 reddedilemez. Varyans homojenliği sağlanmaktadır.

# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz.
# Varsayımla sağlandığı için parametrik test uygulanacak.
pvalue_ttest = stats.ttest_ind(df.loc[df["Group"] == "Test", "Purchase"],
                                df.loc[df["Group"] == "Control", "Purchase"],
                                equal_var=True)[1]
print(pvalue_ttest) # 0.34932579202108416 => H0 reddedilemez.

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma ortalamaları arasında istatistiki
# olarak anlamlı bir fark olup olmadığını yorumlayınız.
# pvalue =  0.34932579202108416, pvalue > 0.05 olduğundan H0 reddedilemez.

# Görev 4: Sonuçların Analizi
# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.
# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.
# Bağımsız iki örneklem t test için gerekli olan varsayımlar sağlandığı için parametrik test olan t testi kullanılmıştır.
# Varsayımlar sağlanmasaydı nonparametrik test olan mannwhitneyu testi kullanılabilirdi
# H0 hipotezini reddedemediğimiz için iki grup satın alma ortalaması arasında istatistiksel olarak anlamlı fark vardır diyemeyiz.
# Satın alma anlamında anlamlı bir fark olmadığından müşteri iki yöntemden birini seçebilir fakat burada diğer istatistiklerdeki
# farklılıklar da önemlidir. Tıklanma, etkileşim, kazanç ve dönüşüm oranlarındaki farklılıklar değerlendirilip hangi yöntemin daha
# kazançlı olduğu tespit edilebilir. Özellikle Facebook'a tıklama başına para ödendiği için hangi yöntemde tıklanma oranının daha düşük
# olduğu tespit edilip ve CTR (tıklama oranı) bakılablir. İki grup gözlenmeye devam edilir.