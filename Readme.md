https://habrahabr.ru/post/167479/

[kotsareu@kotsareu ~]$ sudo apt-get install swig bison ffmpeg -y

[kotsareu@kotsareu sphinxbase-5prealpha]$ chmod +x ./configure
[kotsareu@kotsareu sphinxbase-5prealpha]$ ./configure 
[kotsareu@kotsareu sphinxbase-5prealpha]$ sudo make install 

[kotsareu@kotsareu pocketsphinx-5prealpha]$ chmod +x configure
[kotsareu@kotsareu pocketsphinx-5prealpha]$ sudo ./configure
[kotsareu@kotsareu pocketsphinx-5prealpha]$ sudo make install



[kotsareu@kotsareu cmuclmtk-0.7]$ chmod +x configure
[kotsareu@kotsareu cmuclmtk-0.7]$ ./configure
[kotsareu@kotsareu cmuclmtk-0.7]$ sudo make install 
[kotsareu@kotsareu cmuclmtk-0.7]$ sudo ldconfig

[kotsareu@kotsareu python]$ cat lmbase.txt 
<s> привет </s>
<s> как </s>
<s> дела </s>
<s> русский </s>

[kotsareu@kotsareu python]$ text2wfreq <lmbase.txt | wfreq2vocab> lmbase.tmp.vocab
[kotsareu@kotsareu python]$ cp lmbase.tmp.vocab lmbase.vocab
[kotsareu@kotsareu python]$ text2idngram -vocab lmbase.vocab -idngram lmbase.idngram < lmbase.txt
[kotsareu@kotsareu python]$ idngram2lm -vocab_type 0 -idngram lmbase.idngram -vocab lmbase.vocab -arpa lmbase.arpa
[kotsareu@kotsareu python]$ sphinx_lm_convert -i lmbase.arpa -o lmbase.lm.DMP

[kotsareu@kotsareu python]$  git clone https://github.com/zamiron/ru4sphinx/
[kotsareu@kotsareu python]$ vim test_dictionary
[kotsareu@kotsareu python]$ cat test_dictionary 
привет
как
дела
русский
[kotsareu@kotsareu cmusphinx-ru-5.2]$ python dictionary.py test_dictionary 
привет p rj i0 vj e0 t
как k a0 k
дела dj e0 l a0
русский r u0 s s kj i0 j
[kotsareu@kotsareu cmusphinx-ru-5.2]$ vim my_dict.dic
 пишем туда свою модель
копируем все файлы, созданные в процессе настройки в папку с cmusphinx-ru-5.2
