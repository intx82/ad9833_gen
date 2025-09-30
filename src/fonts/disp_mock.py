class disp_mock:
    def pixel(self, x, y, c):
        print('Pixel: ', x,y,c)
    
    def rect(self,x,y,w,h,c):
        print('Rect: ', x,y,w,h,c)
