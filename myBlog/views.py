from django.shortcuts import render,get_object_or_404,redirect
from .models import Post,Category,Tag
from markdown import markdown,Markdown
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.http import HttpResponse
from comment.forms import CommentForm
from django.views.generic import ListView,DetailView

# def index(request):
#     post_list = Post.objects.all().order_by('-created_time')
#     return render(request,'myBlog/index.html',context={'post_list':post_list})
    # return HttpResponse('<h1>hello world</h1>')
class IndexView(ListView):
    model = Post
    template_name = 'myBlog/index.html'
    context_object_name = 'post_list' # 这个name不能瞎取，必须和模板中的变量一致
    paginate_by = 2

    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            return {}

        # 设置默认值
        # 1、first是首页
        first = False
        #\2、省略号
        left_has_more = False
        #\3、当前页左边的几个页码
        left = []
        # 4、当前页的页码
        page_number = page.number
        #\5、当前页右边的几个页码
        right = []
        #\6、省略号
        right_has_more = False
        #\7、last是最后一页
        last = False

        # 总页数
        total_pages = paginator.num_pages

        # 获取整个分页页码列表。例如共有10页时，page_range:[1,2,3,4,5,6,7,8,9,10]
        page_range = paginator.page_range

        # 如果当前是第1页
        if page_number == 1:
            right = page_range[page_number:page_number+1]
            if right[-1]<total_pages-1:
                right_has_more = True
            if right[-1]<total_pages:
                last = True
        elif page_number == total_pages: # 如果当前是最后一页
            left = page_range[(page_number-2) if (page_number-2)>0 else 0:page_number-1]
            if left[0]>2:
                left_has_more = True
            if left[0]>1:
                first = True
        else:
            left = page_range[(page_number-2) if (page_number-2)>0 else 0:page_number-1]
            right = page_range[page_number:page_number+1]
            if right[-1]<total_pages-1:
                right_has_more = True
            if right[-1]<total_pages:
                last = True
            if left[0]>2:
                left_has_more = True
            if left[0]>1:
                first = True
        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }

        return data

    def get_context_data(self, **kwargs):
        # 首先获得基类get_context_data()返回的context
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator,page,is_paginated)

        context.update(pagination_data)

        return context

# def detail(request,pk):
#     post = get_object_or_404(Post,pk=pk)
#     post.body = markdown(post.body, extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         'markdown.extensions.toc', ])
#     form = CommentForm()
#     comment_list = post.comment_set.all()
#     context = {
#         'post': post,
#         'form': form,
#         'comment_list': comment_list,
#     }
#     return render(request,'myBlog/detail.html',context={'post':post})

class PostDetailView(DetailView):
    model = Post
    template_name = 'myBlog/detail.html'
    context_object_name = 'post'

    def get(self,request,*args,**kwargs):
        response = super().get(request,*args,**kwargs)
        self.object.increase_views() # self.object实际上是Post的对象
        return response

    def get_object(self,queryset=None):
        post = super().get_object(queryset)
        md = Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 把post加到context
        form = CommentForm()
        # 下面的self.object是由self.get_object()得到的
        # 因此self.get_object()必须返回post
        comment_list = self.object.comment_set.all()
        context.update({   # context已有post了，所以这里使用更新update
            'form':form,
            'comment_list':comment_list,
        })
        return context

#
# def archives(request,year,month):
#     post_list = Post.objects.filter(created_time__year=year,
#                                     created_time__month=month)
#     return render(request,'myBlog/index.html',context={'post_list':post_list})

#get_queryset(self)  默认取出该表所有数据。想要过滤自定义只能在get_queryset()中
class ArchivesView(IndexView):
    #复写函数，获取子集并过滤
    def get_queryset(self):
        return super().get_queryset().filter(
            created_time__year = self.kwargs.get('year'),
            created_time__month = self.kwargs.get('month')
        )

# def category(request,pk):
#     cate = get_object_or_404(Category,pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request,'myBlog/index.html',context={'post_list':post_list})

class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        # 下面filter(category=cate)中的category是post.category
        return super().get_queryset().filter(category=cate)

class TagView(IndexView):
    def get_queryset(self):
        context = get_object_or_404(Tag,pk = self.kwargs.get('pk'))
        return super().get_queryset().filter(tag = context)


from .forms import PostForm
def report(request):

    form = PostForm(request.POST)
    return render(request,'myBlog/report_article.html',context={'form': form})

def saveArticle(request):
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            form = PostForm()
        return render(request, 'myBlog/report_article.html', context={'form': form})
