import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import re
import sys
import threading
import time

class PDFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFサイズ制限対応分割ツール")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        self.pdf_path = None
        self.output_dir = None
        
        # サイズ制限の設定変数
        self.size_value = tk.IntVar(value=5)  # デフォルト値
        self.size_unit = tk.StringVar(value="MB")  # デフォルト単位
        self.unit_factors = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}
        
        self.pdf_info = tk.StringVar(value="PDFファイルを選択してください")
        
        # 実行ボタン状態管理用変数
        self.execute_button_enabled = tk.BooleanVar(value=False)
        
        # 処理状態表示用
        self.processing_status = tk.StringVar(value="準備完了")
        
        self._create_widgets()
    
    def _create_widgets(self):
        # メインフレーム
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ファイル選択セクション
        file_frame = ctk.CTkFrame(self.main_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(file_frame, text="PDFファイル:").pack(side="left", padx=5)
        
        self.file_path_label = ctk.CTkLabel(file_frame, text="選択されていません")
        self.file_path_label.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(file_frame, text="参照...", command=self._browse_pdf).pack(side="right", padx=5)
        
        # 出力先選択セクション
        output_frame = ctk.CTkFrame(self.main_frame)
        output_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(output_frame, text="出力先:").pack(side="left", padx=5)
        
        self.output_path_label = ctk.CTkLabel(output_frame, text="選択されていません（デフォルト：PDFと同じ場所）")
        self.output_path_label.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(output_frame, text="参照...", command=self._browse_output_dir).pack(side="right", padx=5)
        
        # サイズ制限セクション
        size_frame = ctk.CTkFrame(self.main_frame)
        size_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(size_frame, text="ファイルサイズ制限:").pack(anchor="w", padx=5, pady=5)
        
        # ダイアル式設定フレーム
        dial_frame = ctk.CTkFrame(size_frame)
        dial_frame.pack(fill="x", padx=5, pady=5)
        
        # 数値選択ダイアル
        value_frame = ctk.CTkFrame(dial_frame)
        value_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkLabel(value_frame, text="値:").pack(pady=2)
        
        value_options_frame = ctk.CTkFrame(value_frame)
        value_options_frame.pack(fill="x", pady=5)
        
        # 数値を減らすボタン
        ctk.CTkButton(
            value_options_frame, 
            text="-", 
            width=30, 
            command=self._decrease_value
        ).pack(side="left", padx=5)
        
        # 数値入力フィールドを追加
        self.value_entry = ctk.CTkEntry(
            value_options_frame,
            width=60,
            justify="center",
            font=("Helvetica", 14, "bold")
        )
        self.value_entry.insert(0, str(self.size_value.get()))
        self.value_entry.pack(side="left", padx=5)
        # キーボード入力の確定は行わない（実行ボタン押下時に反映）
        
        # 数値を増やすボタン
        ctk.CTkButton(
            value_options_frame, 
            text="+", 
            width=30, 
            command=self._increase_value
        ).pack(side="left", padx=5)
        
        # PDF情報更新ボタン
        ctk.CTkButton(
            value_options_frame,
            text="更新",
            width=60,
            command=self._validate_and_update_info
        ).pack(side="left", padx=10)
        
        # 単位選択ダイアル
        unit_frame = ctk.CTkFrame(dial_frame)
        unit_frame.pack(side="right", padx=10)
        
        ctk.CTkLabel(unit_frame, text="単位:").pack(pady=2)
        
        # 単位選択用のオプションメニュー
        unit_menu = ctk.CTkOptionMenu(
            unit_frame,
            values=["KB", "MB", "GB"],
            variable=self.size_unit,
            command=self._update_size_info
        )
        unit_menu.pack(fill="x", pady=5)
        unit_menu.set(self.size_unit.get())
        
        # 情報表示エリア
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="PDFファイル情報:").pack(anchor="w", padx=5, pady=5)
        
        self.info_label = ctk.CTkLabel(info_frame, textvariable=self.pdf_info, wraplength=550, justify="left")
        self.info_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 実行ボタン
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # 実行ボタンを初期状態では無効にする
        self.execute_button = ctk.CTkButton(
            button_frame, 
            text="実行", 
            command=self._execute_processing, 
            fg_color="#28a745", 
            hover_color="#218838",
            state="disabled"  # 初期状態では無効
        )
        self.execute_button.pack(padx=5, pady=5, fill="x")
        
        # 処理状況表示用フレーム（初期状態では非表示）
        self.processing_frame = ctk.CTkFrame(self.root)
        
    def _validate_entry(self):
        """入力された値を検証して適切な形式に変換する"""
        entry_text = self.value_entry.get()
        
        # 全角数字を半角に変換
        zen_to_han = str.maketrans('０１２３４５６７８９', '0123456789')
        entry_text = entry_text.translate(zen_to_han)
        
        # 数字以外の文字を除去
        entry_text = re.sub(r'[^0-9]', '', entry_text)
        
        # 空の場合またはすべて数字以外だった場合はエラー
        if not entry_text:
            messagebox.showerror("エラー", "有効な数値が入力されていません。\n数字を含む値を入力してください。")
            return False
        
        # 値を整数に変換
        try:
            value = int(entry_text)
            
            # 単位に応じた最大値を設定
            if self.size_unit.get() == "KB":
                max_value = 10000
            elif self.size_unit.get() == "MB":
                max_value = 1000
            else:  # GB
                max_value = 10
                
            # 範囲内に収める
            value = max(1, min(value, max_value))
            
            self.size_value.set(value)
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, str(value))
            
            return True
            
        except ValueError:
            # 変換エラーの場合はエラーメッセージを表示
            messagebox.showerror("エラー", "数値の変換に失敗しました。\n有効な数字を入力してください。")
            return False
    
    def _validate_and_update_info(self):
        """入力値を検証してPDF情報を更新する"""
        if self._validate_entry():
            self._update_pdf_info()
            self._update_execute_button_state()
    
    def _increase_value(self):
        """サイズ値を増加させる (常に1単位で増加)"""
        if not self._validate_entry():
            return
            
        current = self.size_value.get()
        
        if self.size_unit.get() == "KB":
            max_value = 10000  # KBの最大値
        elif self.size_unit.get() == "MB":
            max_value = 1000  # MBの最大値
        else:  # GB
            max_value = 10  # GBの最大値
            
        if current < max_value:
            # 常に1単位ずつ増加
            new_value = current + 1
            self.size_value.set(new_value)
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, str(new_value))
            self._update_pdf_info()
            
            # ボタン状態の更新
            self._update_execute_button_state()
    
    def _decrease_value(self):
        """サイズ値を減少させる (常に1単位で減少)"""
        if not self._validate_entry():
            return
            
        current = self.size_value.get()
        
        if current > 1:
            # 常に1単位ずつ減少
            new_value = current - 1
            self.size_value.set(new_value)
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, str(new_value))
            self._update_pdf_info()
            
            # ボタン状態の更新
            self._update_execute_button_state()
    
    def _update_size_info(self, *args):
        """サイズ情報を更新（単位変更時のみ）"""
        if self.pdf_path:
            self._validate_entry()  # 現在の値を検証
            self._update_pdf_info()
            
            # ボタン状態の更新
            self._update_execute_button_state()
    
    def _browse_pdf(self):
        file_path = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDFファイル", "*.pdf")]
        )
        
        if file_path:
            self.pdf_path = file_path
            self.file_path_label.configure(text=os.path.basename(file_path))
            self._update_pdf_info()
            
            # ボタン状態の更新
            self._update_execute_button_state()
    
    def _browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="出力先フォルダを選択")
        
        if dir_path:
            self.output_dir = dir_path
            self.output_path_label.configure(text=dir_path)
    
    def _update_execute_button_state(self):
        """実行ボタンの状態を更新"""
        # ファイルが選択されていて、サイズ制限値が有効であれば実行ボタンを有効化
        if self.pdf_path and self.size_value.get() > 0:
            self.execute_button.configure(state="normal")
        else:
            self.execute_button.configure(state="disabled")
    
    def _get_size_limit_in_bytes(self):
        """現在の設定から制限サイズをバイト単位で取得"""
        value = self.size_value.get()
        unit = self.size_unit.get()
        return value * self.unit_factors[unit]
        
    def _update_pdf_info(self):
        if not self.pdf_path:
            self.pdf_info.set("PDFファイルを選択してください")
            return
        
        try:
            pdf_size_bytes = os.path.getsize(self.pdf_path)
            pdf_size_mb = pdf_size_bytes / (1024 * 1024)
            
            reader = PdfReader(self.pdf_path)
            page_count = len(reader.pages)
            
            info = f"ファイル名: {os.path.basename(self.pdf_path)}\n"
            info += f"ページ数: {page_count} ページ\n"
            info += f"ファイルサイズ: {pdf_size_mb:.2f} MB\n"
            
            # 現在の設定からサイズ制限を計算
            size_limit_bytes = self._get_size_limit_in_bytes()
            size_limit_mb = size_limit_bytes / (1024 * 1024)
            
            if pdf_size_bytes <= size_limit_bytes:
                info += f"\n現在のサイズ制限（{self.size_value.get()} {self.size_unit.get()}）を超えていないため、分割は不要です。"
            else:
                estimated_parts = max(2, int(pdf_size_bytes / size_limit_bytes) + 1)
                avg_pages_per_part = page_count // estimated_parts
                
                info += f"\n現在のサイズ制限（{self.size_value.get()} {self.size_unit.get()}）を超えています。\n"
                info += f"推定分割数: 約{estimated_parts}部（各部約{avg_pages_per_part}ページ）"
            
            self.pdf_info.set(info)
            
        except Exception as e:
            self.pdf_info.set(f"エラー: PDFファイルの読み込みに失敗しました。\n{str(e)}")
    
    def _show_processing_screen(self):
        """処理中画面を表示"""
        # 既存のフレームを削除
        self.main_frame.pack_forget()
        
        # 処理状況表示フレームを作成
        self.processing_frame = ctk.CTkFrame(self.root)
        self.processing_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        ctk.CTkLabel(
            self.processing_frame, 
            text="PDF分割処理中...", 
            font=("Helvetica", 20, "bold")
        ).pack(pady=(20, 30))
        
        # ファイル情報
        file_info = f"ファイル: {os.path.basename(self.pdf_path)}\n"
        file_info += f"サイズ制限: {self.size_value.get()} {self.size_unit.get()}"
        ctk.CTkLabel(
            self.processing_frame,
            text=file_info,
            justify="left",
            wraplength=550
        ).pack(pady=10, fill="x")
        
        # 進行状況表示
        status_frame = ctk.CTkFrame(self.processing_frame)
        status_frame.pack(fill="x", padx=20, pady=20, expand=True)
        
        ctk.CTkLabel(
            status_frame,
            textvariable=self.processing_status,
            font=("Helvetica", 14),
            wraplength=550,
            justify="center"
        ).pack(pady=30)
    
    def _execute_processing(self):
        """実行ボタンが押されたときの処理"""
        # 入力された値を検証
        if not self._validate_entry():
            return
        
        # 処理画面に切り替え
        self._show_processing_screen()
        
        # 処理を別スレッドで実行
        threading.Thread(target=self._process_pdf, daemon=True).start()
    
    def _process_pdf(self):
        if not self.pdf_path:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        try:
            self.processing_status.set("PDFファイルのサイズを確認中...")
            
            pdf_size_bytes = os.path.getsize(self.pdf_path)
            size_limit_bytes = self._get_size_limit_in_bytes()
            
            # サイズ制限を超えていない場合は処理しない
            if pdf_size_bytes <= size_limit_bytes:
                self.processing_status.set("PDFファイルは既にサイズ制限以内です。分割の必要はありません。")
                self.root.after_idle(lambda: messagebox.showinfo(
                    "情報", 
                    f"PDFファイルは既にサイズ制限（{self.size_value.get()} {self.size_unit.get()}）以内です。分割の必要はありません。"
                ))
                # プログラム終了
                self.root.after(1000, self.root.destroy)
                return
            
            # 出力先の決定
            output_directory = self.output_dir if self.output_dir else os.path.dirname(self.pdf_path)
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            
            self.processing_status.set("PDFファイルを読み込み中...")
            reader = PdfReader(self.pdf_path)
            total_pages = len(reader.pages)
            
            # バイナリサーチを使って最適な分割点を見つける
            self.processing_status.set("最適な分割点を計算中...")
            result = self._find_optimal_splits(reader, total_pages, size_limit_bytes)
            
            if not result:
                self.processing_status.set("エラー: PDFの分割に失敗しました。")
                self.root.after_idle(lambda: messagebox.showerror("エラー", "PDFの分割に失敗しました。"))
                # プログラム終了
                self.root.after(1000, self.root.destroy)
                return
            
            # 分割実行
            split_points = result
            num_parts = len(split_points) - 1  # 分割点の数から実際の分割数を計算
            
            for i in range(num_parts):
                # UIの更新はメインスレッドで行う
                status_msg = f"分割ファイル {i+1}/{num_parts} を作成中..."
                self.root.after_idle(lambda s=status_msg: self.processing_status.set(s))
                
                start_page = split_points[i]
                end_page = split_points[i+1] if i+1 < len(split_points) else total_pages
                
                writer = PdfWriter()
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                output_file = os.path.join(output_directory, f"{base_name}_part{i+1}.pdf")
                with open(output_file, "wb") as f:
                    writer.write(f)
                
                # 進捗を表示（スレッドセーフ）
                complete_msg = f"分割ファイル {i+1}/{num_parts} を作成しました"
                self.root.after_idle(lambda s=complete_msg: self.processing_status.set(s))
                
                # 少し待機して次の処理へ
                time.sleep(0.5)
            
            final_msg = f"完了: PDFファイルを{num_parts}つに分割しました"
            self.root.after_idle(lambda s=final_msg: self.processing_status.set(s))
            
            # 完了メッセージを表示（スレッドセーフ）
            self.root.after_idle(lambda: messagebox.showinfo("成功", 
                f"PDFファイルを{num_parts}つに分割しました。\n保存先: {output_directory}"))
            
            # プログラム終了（スレッドセーフ）- 少し遅延させて他のコールバックが処理される時間を確保
            self.root.after(1000, self.root.destroy)
            
        except Exception as e:
            error_msg = f"処理中にエラーが発生しました。\n{str(e)}"
            self.root.after_idle(lambda s=error_msg: self.processing_status.set(f"エラー: {s}"))
            # エラーメッセージを表示（スレッドセーフ）
            self.root.after_idle(lambda e=error_msg: messagebox.showerror("エラー", e))
            # プログラム終了（スレッドセーフ）
            self.root.after(1000, self.root.destroy)
    
    def _find_optimal_splits(self, reader, total_pages, size_limit_bytes):
        """バイナリサーチを使って最適な分割点を見つける"""
        splits = [0]  # 最初のページは常に0
        current_start = 0
        
        while current_start < total_pages:
            # 進捗状況の更新 - lambdaでローカル変数をキャプチャせず、直接文字列を渡す
            progress_msg = f"分割点を計算中... ({current_start}/{total_pages} ページ)"
            # スレッドセーフなGUI更新
            self.root.after_idle(lambda s=progress_msg: self.processing_status.set(s))
            
            # バイナリサーチで次の分割点を探す
            low = current_start + 1
            high = total_pages
            best_end = low
            
            while low <= high:
                mid = (low + high) // 2
                
                # 現在のページ範囲のサイズをチェック
                size = self._estimate_pdf_size(reader, current_start, mid)
                
                if size <= size_limit_bytes:
                    best_end = mid
                    low = mid + 1
                else:
                    high = mid - 1
            
            # 進展がなければ（1ページでもサイズ制限を超える場合）
            if best_end <= current_start:
                return None
                
            splits.append(best_end)
            current_start = best_end
            
            # 最後のページに到達したら終了
            if best_end >= total_pages:
                break
                
        return splits
    
    def _estimate_pdf_size(self, reader, start_page, end_page):
        """指定範囲のPDFのサイズを推定する"""
        # 一時ファイルに書き出して実際のサイズを計算
        writer = PdfWriter()
        for i in range(start_page, end_page):
            writer.add_page(reader.pages[i])
            
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            writer.write(tmp)
            tmp.flush()
            size = os.path.getsize(tmp.name)
            
        return size


def main():
    root = ctk.CTk()
    app = PDFSplitterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
