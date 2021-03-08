# 古書邂逅 協調フィルタリング高速化用API
"古書邂逅"(<https://github.com/HEW2meiG/HEW2>)協調フィルタリング高速化用APIです。

1分毎にレコメンド用のデータの加工を行い、リクエストがきたら加工済みデータを返すAPIです。

![図](https://github.com/HEW2meiG/set_prefs/blob/images/figure.png)

データ加工に読み込み時間が6秒ほどかかっていましたが、このAPIを用いることで、瞬時にレコメンドを行うことができるようになりました。
