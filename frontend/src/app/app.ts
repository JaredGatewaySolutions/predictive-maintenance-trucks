import { Component, signal, ViewChild, OnInit, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule, MatSidenav } from '@angular/material/sidenav';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  @ViewChild('sidenav') sidenav!: MatSidenav;

  private breakpointObserver = inject(BreakpointObserver);

  protected readonly title = signal('Armored Brigade Combat Team - Predictive Maintenance');
  protected readonly isMobile = signal(false);
  protected readonly sidenavMode = signal<'over' | 'side'>('side');
  protected readonly sidenavOpened = signal(true);

  ngOnInit() {
    // Listen for breakpoint changes
    this.breakpointObserver.observe([
      Breakpoints.XSmall,
      Breakpoints.Small
    ]).subscribe(result => {
      const mobile = result.matches;
      this.isMobile.set(mobile);
      this.sidenavMode.set(mobile ? 'over' : 'side');
      this.sidenavOpened.set(!mobile);
    });
  }

  toggleSidenav() {
    this.sidenav.toggle();
  }

  closeSidenavOnMobile() {
    if (this.isMobile()) {
      this.sidenav.close();
    }
  }
}
