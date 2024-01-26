/**
 * Treeview (jquery)
 */

'use strict';

$(function () {
  var theme = $('html').hasClass('light-style') ? 'default' : 'default-dark',
    basicTree = $('#jstree-basic'),
    customIconsTree = $('#jstree-custom-icons'),
    contextMenu = $('#jstree-context-menu'),
    dragDrop = $('#jstree-drag-drop'),
    checkboxTree = $('#jstree-checkbox'),
    ajaxTree = $('#jstree-ajax');

  // Basic
  // --------------------------------------------------------------------
  if (basicTree.length) {
    basicTree.jstree({
      core: {
        themes: {
          name: theme
        }
      }
    });
  }

  // Custom Icons
  // --------------------------------------------------------------------
  if (customIconsTree.length) {
    customIconsTree.jstree({
      core: {
        themes: {
          name: theme
        },
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }

  // Context Menu
  // --------------------------------------------------------------------
  if (contextMenu.length) {
    contextMenu.jstree({
      core: {
        themes: {
          name: theme
        },
        check_callback: true,
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types', 'contextmenu'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }

  // Drag Drop
  // --------------------------------------------------------------------
  if (dragDrop.length) {
    dragDrop.jstree({
      core: {
        themes: {
          name: theme
        },
        check_callback: true,
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types', 'dnd'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }

  // Checkbox
  // --------------------------------------------------------------------
  $.ajax({
    url: "/admins/node_info/", // 사용자 정보를 제공하는 API의 URL
    method: "GET",
    dataType: "json",
    success: function(data) {
      // console.log('member', data)

      // ID=키 name=값 객체변환
      var codeMasterMap = data.code_data.reduce(function (result, item) {
        result[item.pk] = item.fields.name;
        return result;
      }, {});

      // 부서별 그룹
      var groupedData = data.user_data.reduce(function (result, user) {
        var departmentId = user.fields.department_position;
        if (!result[departmentId]) {
          result[departmentId] = [];
        }
        result[departmentId].push(user);
        return result;
      }, {});

      var treeData = [];



      //  console.log('codemaster : ',codeMasterMap);
      // 각 그룹에 대해 폴더 노드를 만들고 사용자 노드를 추가
      for (var departmentId in groupedData) {
        var departmentUsers = groupedData[departmentId];
        // 폴더 노드 추가
        treeData.push({
          id: 'd_' + departmentId,
          parent: '#',
          text: codeMasterMap[departmentId], // 부서 이름으로 변환
          type: 'department'
        });

        departmentUsers.sort(function (a, b) {
          if (a.fields.job_position < b.fields.job_position) {
            return -1;
          }
          if (a.fields.job_position > b.fields.job_position) {
            return 1;
          }
          return 0;
        });

        // 사용자 노드 추가
        departmentUsers.forEach(function (user) {
          treeData.push({
            id: user.pk,
            parent: 'd_' + departmentId,
            text: user.fields.username + ' (' + codeMasterMap[user.fields.job_position] + ')', // 직급 이름으로 변환
            type: 'user'
          });

        });
      }

      checkboxTree.jstree({
        core: {
          themes: {
            name: theme
          },
          data: treeData
        },
        plugins: ['types', 'checkbox', 'wholerow'],
        types: {
          default: {
            icon: 'bx bx-folder'
          },
          department: {
            icon: 'bx bx-folder'
          },
          user: {
            icon: 'bx bx-user'
          },
          html: {
            icon: 'bx bxl-html5 text-danger'
          },
          css: {
            icon: 'bx bxl-css3 text-info'
          },
          img: {
            icon: 'bx bx-image text-success'
          },
          js: {
            icon: 'bx bxl-nodejs text-warning'
          }
        }
      }).on('ready.jstree', function () {
        // 체크된 노드 추출
        var checkedNodes = $('#jstree-checkbox').jstree('get_checked', true);

        // 체크된 노드를 treeData로 변환
        var treeData = checkedNodes.map(function (node) {
          return {
            id: node.id,
            parent: node.parent,
            text: node.text,
            type: node.type
          };
        });

        // treeData를 전역 변수에 저장
        window.treeData = treeData;
      });
    }
  })

  // if (checkboxTree.length) {
  //   checkboxTree.jstree({
  //     core: {
  //       themes: {
  //         name: theme
  //       },
  //       data: [
  //         {
  //           text: 'css',
  //           children: [
  //             {
  //               text: 'app.css',
  //               type: 'css'
  //             },
  //             {
  //               text: 'style.css',
  //               type: 'css'
  //             }
  //           ]
  //         },
  //         {
  //           text: 'img',
  //           state: {
  //             opened: true
  //           },
  //           children: [
  //             {
  //               text: 'bg.jpg',
  //               type: 'img'
  //             },
  //             {
  //               text: 'logo.png',
  //               type: 'img'
  //             },
  //             {
  //               text: 'avatar.png',
  //               type: 'img'
  //             }
  //           ]
  //         },
  //         {
  //           text: 'js',
  //           state: {
  //             opened: true
  //           },
  //           children: [
  //             {
  //               text: 'jquery.js',
  //               type: 'js'
  //             },
  //             {
  //               text: 'app.js',
  //               type: 'js'
  //             }
  //           ]
  //         },
  //         {
  //           text: 'index.html',
  //           type: 'html'
  //         },
  //         {
  //           text: 'page-one.html',
  //           type: 'html'
  //         },
  //         {
  //           text: 'page-two.html',
  //           type: 'html'
  //         }
  //       ]
  //     },
  //     plugins: ['types', 'checkbox', 'wholerow'],
  //     types: {
  //       default: {
  //         icon: 'bx bx-folder'
  //       },
  //       html: {
  //         icon: 'bx bxl-html5 text-danger'
  //       },
  //       css: {
  //         icon: 'bx bxl-css3 text-info'
  //       },
  //       img: {
  //         icon: 'bx bx-image text-success'
  //       },
  //       js: {
  //         icon: 'bx bxl-nodejs text-warning'
  //       }
  //     }
  //   });
  // }

  // Ajax Example
  // --------------------------------------------------------------------
  if (ajaxTree.length) {
    ajaxTree.jstree({
      core: {
        themes: {
          name: theme
        },
        data: {
          url: assetsPath + 'json/jstree-data.json',
          dataType: 'json',
          data: function (node) {
            return {
              id: node.id
            };
          }
        }
      },
      plugins: ['types', 'state'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }
});
