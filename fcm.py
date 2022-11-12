from pyfcm import FCMNotification

APIKEY = "AAAALjuSJyE:APA91bGroTQePiP4c1UILDHsLjmJP5Vo3ytdYeQIJMMnpl9ysnMxBlTJVyfKpWEQc8HCEyzlxN84r3HRDBu288qqE6JFAwsiPiMjzMMgXx6EuuiLB1TNbLhhJFzW2SLBJJedwHsBSbUA"
TOKEN = "eayHPHmFTcCCQaBLSATSoC:APA91bEvEOqz64sqg9KCXdTkns6ZSyYFTYQGSmrIVfucgITRApzINs05eoaVkXA58rvQSRh91zaokrDo0VudgAu2IfMmJsg9g8mQbWlfyFevlVk4T6Xww7MIL_0Rg7WDN0Ewb7-kLTny"
 
# 파이어베이스 콘솔에서 얻어 온 서버 키를 넣어 줌
push_service = FCMNotification(APIKEY)
 
def sendMessage(body, title):
    # 메시지 (data 타입)
    data_message = {
        "body": body,
        "title": title
    }
 
    # 토큰값을 이용해 1명에게 푸시알림을 전송함
    result = push_service.single_device_data_message(registration_id=TOKEN, data_message=data_message)
 
    # 전송 결과 출력
    print(result)
 
sendMessage("Title Example", "Body Example")