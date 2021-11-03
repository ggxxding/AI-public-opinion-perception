if __name__ == '__main__':


    for page in range(10,20):#循环页面
        try:
            results=range(5)
            for result in results:
                if result == 3:
                    result=result[0]
                    print('继续')
                    continue
                print(result)
        except TypeError:
            print("格式错误，跳过")
            continue